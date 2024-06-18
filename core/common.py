import json
import math
import matplotlib.colors as colors
import numbers
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from core.inputs import InputSet


class DataSource:
    """
    A `DataSource` is a mixin for reading data from a CSV file.
    Requires that `self.table` be a path to a CSV file.
    """

    # these can be overridden in subclasses
    filters = [
        # example: will filter data rows down to those with `column_name` equal to `example`:
        # ('column_name', 'example'),
    ]

    def data_frame(self):
        if not hasattr(self, '_df'):
            self._df = None

        if self._df is None and self.table is not None:
            df = pd.read_csv(self.table)
            for field, value in type(self).filters:
                df = df[df[field] == value]
            self._df = df

        return self._df


class InputSource:
    """
    An `InputSource` is a class that declares and uses a set of user inputs.
    """

    @classmethod
    def user_inputs(cls):
        # DEPRECATED: please implement `inputs` instead
        return []

    @classmethod
    def inputs(cls):
        # this should be overridden in child classes
        return cls.user_inputs()

    @classmethod
    def input_set(cls, values):
        return InputSet(cls.inputs(), values)

    @classmethod
    def instantiate(cls, values):
        input_set = cls.input_set(values)
        inst = cls()
        inst.prepare(input_set)
        return inst

    def prepare(self, input_set):
        self.input_set = input_set

        # TODO: I'd like to deprecate this and always access input values
        # via `self.input_set.input_value(input_name)` so that it's clear where
        # the value is coming from
        for input_name in self.input_set.inputs.keys():
            value = self.input_set.value(input_name)
            setattr(self, input_name, value)

    @property
    def input_values(self):
        res = {}
        for input_name in self.input_set.input_names:
            value = self.input_value(input_name)
            if value is not None:
                res[input_name] = value
        return res

    def input_value(self, input_name, default=True):
        if input_name not in self.input_set.inputs:
            raise Exception(f'unknown input: {input_name}')
        return self.input_set.value(input_name, default=default)

    # only applicable for instances that are also a `DataSource`
    def filtered_data_frame(self):
        df = self.data_frame()

        for input_name, input in self.input_set.inputs.items():
            value = self.input_set.value(input_name, default=False)
            if value is not None and input.input_type == 'categorical':
                if is_numeric_dtype(df[input.label].dtype):
                    value = float(value)
                df = df[df[input.label] == value]

        return df

    def categorical_options(self, input):
        df = self.filtered_data_frame()
        return [
            x for x in df[input.label].unique()
            if not isinstance(x, numbers.Number) or not math.isnan(x)
        ]


class Versioned:
    version = 1


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.integer) or isinstance(obj, np.floating):
            return self._value(obj)
        elif isinstance(obj, np.ndarray):
            return [
                self._value(value)
                for value in obj.tolist()
            ]
        elif isinstance(obj, pd.DataFrame):
            return [
                [
                    self._value(value)
                    for value in item.tolist()
                ]
                for item in obj.to_numpy()
            ]
        elif isinstance(obj, pd.Series):
            return [
                self._value(value)
                for value in obj.to_numpy().tolist()
            ]
        elif isinstance(obj, Color):
            return repr(obj)
        else:
            return super(JSONEncoder, self).default(obj)

    def _value(self, value):
        if value is None:
            return None
        elif isinstance(value, numbers.Number) and math.isnan(value):
            return None
        elif value == np.nan or value == math.inf or value == np.inf:
            return None
        elif isinstance(value, np.integer) or isinstance(value, np.int64):
            return self._value(int(value))
        elif isinstance(value, np.floating):
            return self._value(float(value))
        else:
            return value


class Color:

    def __init__(self, hex=None, name=None):
        self.hex = hex
        self.name = name
        assert(self.hex is not None or self.name is not None)

    def __repr__(self):
        if self.hex is not None:
            return self.hex
        if self.name is not None:
            return colors.to_hex(self.name)

    def toJson(self):
        return repr(self)
