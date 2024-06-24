import json
from schematics.exceptions import ValidationError, CompoundError, BaseError

from core import validators

class Default:

    def __init__(self, value, conditionals=None):
        self.value = value
        self.conditionals = conditionals or []

    def __repr__(self):
        return f'Default({self.value}, conditionals={self.conditionals})'

    def serialize(self):
        return {
            'value': json.dumps(self.value),

            'conditionals': [
                conditional.serialize()
                for conditional in self.conditionals
            ]
        }

class Tooltip:

    def __init__(self, content=None, source=None, source_link=None):
        self.content = content
        self.source = source
        self.source_link = source_link

    def serialize(self):
        return {
            'content': self.content,
            'source': self.source,
            'source_link': self.source_link,
        }

class InputNode:
    input_type = 'unknown'

    def __init__(self, name, label, conditionals=None, children=None):
        self.name = name
        self.label = label
        self.conditionals = conditionals or []
        self.children = children or []

    def is_relevant(self, input_set):
        relevant = True
        for conditional in self.conditionals:
            relevant = relevant and conditional.check(input_set)
        return relevant

    def validate(self, value):
        for validator in self.validators:
            validator.validate(value)

    def serialize(self):
        return {
            'type': self.input_type,
            'name': self.name,
            'label': self.label,
            'conditionals': [
                conditional.serialize()
                for conditional in self.conditionals
            ],
            'children': [
                child.serialize()
                for child in self.children
            ],
        }

class InputGroup(InputNode):
    input_type = 'group'

def default_value(node, input_set):
    for default in node.defaults:

        if len(default.conditionals) == 0:
            return default.value
        else:
            for conditional in default.conditionals:
                if conditional.check(input_set):
                    return default.value
    return None

class Input(InputNode):
    input_type = 'input'

    def __init__(self, name, label,
                 unit=None,
                 conditionals=None,
                 children=None,
                 validators=None,
                 defaults=None,
                 tooltip=None,
                 on_change_actions=None):
        super().__init__(name, label, conditionals=conditionals, children=children)
        self.unit = unit
        self.validators = validators or []
        self.defaults = defaults or []
        self.tooltip = tooltip
        self.on_change_actions = on_change_actions or []

    def default_value(self, input_set):
        return default_value(self, input_set)

    def transform(self, value):
        if value == '':
            return None
        else:
            return value

    def serialize(self):
        res = super().serialize()
        res.update({
            'unit': self.unit,
            'validators': [
                validator.serialize()
                for validator in self.validators
            ],
            'defaults': [
                default.serialize()
                for default in self.defaults
            ],
            'tooltip': self.tooltip.serialize() if self.tooltip else None,
            'on_change_actions': self.on_change_actions,
        })
        return res

class ContinuousInput(Input):
    input_type = 'continuous'

    def transform(self, value):
        value = super().transform(value)
        if value is not None and type(value) == str:
            try:
                value = float(value)
            except ValueError:
                pass
        return value

class PercentInput(ContinuousInput):
    """
    PercentInputs accept input values in the range 0 <= value <= 100
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators += [
            validators.numeric(),
            validators.gte(0),
            validators.lte(100),
        ]

class CategoricalInput(Input):
    input_type = 'categorical'

class Option:

    def __init__(self, value, conditionals=[]):
        self.value = value
        self.conditionals = conditionals

    def is_relevant(self, input_set):
        relevant = True
        for conditional in self.conditionals:
            relevant = relevant and conditional.check(input_set)
        return relevant

    def serialize(self):
        return {
            'value': self.value,
            'conditionals': [
                conditional.serialize()
                for conditional in self.conditionals
            ]
        }

def _build_option(value):
    if type(value) == Option:
        return value
    else:
        return Option(value)

class OptionsInput(Input):
    input_type = 'options'

    def __init__(self, *args, **kwargs):
        options = kwargs.pop('options')
        super().__init__(*args, **kwargs)
        self.options = [
            _build_option(option)
            for option in options
        ]

    def relevant_options(self, input_set):
        return [
            option
            for option in self.options
            if option.is_relevant(input_set)
        ]

    def validate(self, value):
        super().validate(value)
        values = [str(option.value) for option in self.options]
        if str(value) not in values:
            raise ValidationError(f'{value} is not a valid option')

    def serialize(self):
        data = super().serialize()
        data['options'] = [
            option.serialize()
            for option in self.options
        ]
        return data

class ShareTableInput(Input):
    input_type = 'share_table'

    class Cell:

        def __init__(self, defaults=None, remainder=None, column_total=None):
            self.defaults = defaults
            self.remainder = remainder
            self.column_total = column_total

        def serialize(self):
            return {
                'defaults': [
                    default.serialize()
                    for default in self.defaults
                ],
                'remainder': self.remainder,
                'column_total': self.column_total,
            }

    class Row:

        def __init__(self, name, cells=None, label=None, tooltip=None):
            self.name = name
            self.label = label or name
            self.cells = cells or []
            self.tooltip = tooltip

        def serialize(self):
            return {
                'name': self.name,
                'label': self.label,
                'tooltip': self.tooltip.serialize() if self.tooltip else None,
                'cells': [
                    cell.serialize()
                    for cell in self.cells
                ]
            }

    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns')
        rows = kwargs.pop('rows')
        super().__init__(*args, **kwargs)
        self.columns = columns
        self.rows = rows

    def default_value(self, input_set):
        def column_defaults(idx):
            return [
                default_value(row.cells[idx], input_set)
                for row in self.rows
            ]

        res = {
            column: column_defaults(idx)
            for idx, column in enumerate(self.columns)
        }
        if len(self.columns) == 1:
            res = res[self.columns[0]]

        return res

    def transform(self, value):
        value = super().transform(value)
        if type(value) == str:
            value = json.loads(value)

        if type(value) == list:
            res = { column: [] for column in self.columns }
            res[self.columns[-1]] = value
            if len(self.columns) == 1:
                res = res[self.columns[0]]

            return res

        return value

    def serialize(self):
        data = super().serialize()
        data['columns'] = self.columns
        data['rows'] = [
            row.serialize()
            for row in self.rows
        ]
        return data

class InputSet:
    """
    An `InputSet` is an ordered set of user inputs together
    with one or more corresponding values.
    """

    @classmethod
    def build_empty(cls, source, values=None, context=None):
        return cls(source.inputs(), values=values, context=context)

    @classmethod
    def build_default(cls, source, context=None, values={}):
        input_set = cls(source.inputs(), context=context)

        for name, value in values.items():
            input_set.set_value(name, value)
        for name in input_set.input_names:
            if name not in values:
                value = input_set.default_value(name)
                input_set.set_value(name, value)

        return input_set

    def __init__(self, inputs, values=None, context=None):
        """
        inputs: list of `Input`s
        values: dict of input name -> value
        """
        self.inputs = {}
        self._add_inputs(inputs)
        self.values = {}
        if values is not None:
            for name in self.inputs:
                value = values.get(name)
                if value is not None:
                    self.set_value(name, value)
        self.context = dict(context or {})

    def __contains__(self, input_name):
        input = self.inputs.get(input_name)
        if input is None:
            return False
        return input.is_relevant(self)

    @property
    def input_names(self):
        return self.inputs.keys()

    def build(self, values):
        """
        Populate `self.values` dict from a given ordered list of input values
        """
        inputs = list(self.inputs.values())

        self.values = {}
        for value in values:
            input = inputs.pop(0)
            while not input.is_relevant(self):
                input = inputs.pop(0)
            self.values[input.name] = value

    def input(self, input_name):
        return self.inputs.get(input_name)

    def value(self, input_name, default=True):
        res = self.values.get(input_name)
        if res is None and default:
            res = self.default_value(input_name)
        return res

    def set_value(self, input_name, value):
        self.values[input_name] = self.inputs[input_name].transform(value)

    def set_values(self, items):
        for input_name, value in items.items():
            self.set_value(input_name, value)

    def default_value(self, input_name):
        """
        Returns the default value for the given `input_name`
        """
        input = self.inputs.get(input_name)
        if input is None:
            return None

        return input.default_value(self)

    def set_default(self, input_name):
        self.set_value(input_name, self.default_value(input_name))

    def validate(self):
        errors = {}

        for input_name, input in self.inputs.items():
            if input.is_relevant(self):
                value = self.value(input_name)
                try:
                    input.validate(value)
                except BaseError as e:
                    errors[input_name] = e

        if len(errors) > 0:
            raise CompoundError(errors)

    def _add_inputs(self, inputs):
        for input in inputs:
            if input.input_type != 'group':
                self.inputs[input.name] = input
            self._add_inputs(input.children.copy())
