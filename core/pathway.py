from collections import defaultdict
from core.common import DataSource, InputSource, Versioned
from core.inputs import InputSet
import analysis.lca as lca
from analysis.sensitivity import SensitivityAnalysis
import pandas as pd

def compute_emissions(pathway, input_sets):
    for step in pathway.steps:
        step.input_set = input_sets[step.source]

    results = lca.run([pathway])
    return results['data']['value'].sum()

class Database:

    def __init__(self):
        self.next_id = 1
        self.records = []
        self.index = {}
        self.counters = defaultdict(lambda: 1)

    def insert(self, record):
        id = record.identifier()
        if id in self.index:
            n = self.counters[id]
            self.counters[id] += 1
            id = '-'.join([id, str(n)])

        if id in self.index:
            raise Exception('duplicate id')

        record.id = id
        self.records.append(record)
        self.index[id] = record

    def find(self, id):
        return self.index.get(id)

stages_db = Database()
activities_db = Database()
sources_db = Database()

class Stage:

    def __init__(self, name):
        self.name = name
        self.activities = []
        self.categories = defaultdict(list)
        self.id = None

    def __str__(self):
        return self.name

    def identifier(self):
        return self.name.lower().replace(' ', '')

    def get_activity(self, name):
        for activity in self.activities:
            if activity.name == name:
                return activity
        return None

    def register_activity(self, name, category=None):
        activity = Activity(self, name, category=category)
        activities_db.insert(activity)
        self.activities.append(activity)
        if category:
            self.categories[category].append(activity)
        return activity

    def get_categories(self):
        return list(self.categories.keys())

    def get_activities_by_category(self, category):
        return self.categories.get(category)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'categories': list(self.categories.keys()),
            'activities': [activity.serialize() for activity in self.activities]
        }


class Activity:

    def __init__(self, stage, name, category=None):
        self.stage = stage
        self.name = name
        self.sources = []
        self.links = []
        self.category = category
        self.id = None

        self.products = set()
        self.product_types = set()
        self.resources = set()

    def __str__(self):
        return self.name

    def identifier(self):
        return '-'.join([self.stage.identifier(), self.name.lower().replace(' ', '')])

    def get_source(self, name):
        for source in self.sources:
            if source.name == name:
                return source
        return None

    def register_source(self, name, cls, table=None):
        source = Source(self, name, cls, table)
        self.sources.append(source)
        sources_db.insert(source)
        return source

    def link(self, *activities):
        for activity in activities:
            self.links.append(activity)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'sources': [source.serialize() for source in self.sources],
            'products': list(self.products),
            'product_types': list(self.product_types),
            'resources': list(self.resources),
        }


class Source:

    def __init__(self, activity, name, cls, lookup_table):
        self.activity = activity
        self.name = name
        self.cls = cls
        self.cls.lookup_table = lookup_table
        self.id = None

    def __call__(self, *args, **kwargs):
        return self.instantiate(*args, **kwargs)

    def __str__(self):
        return self.name

    def identifier(self):
        return '-'.join([self.activity.identifier(), self.name.lower().replace(' ', '')])

    def instantiate(self, **kwargs):
        return self.cls(**kwargs)

    def inputs(self):
        return self.cls.user_inputs()

    def sensitivity(self):
        return self.cls.sensitivity()

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_inputs': [
                input.serialize()
                for input in self.inputs()
            ],
            'version': self.cls.version,
        }

class Metadata:

    def __init__(self):
        self.stages = []

    def get_stage(self, name):
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None

    def register_stage(self, name):
        if self.get_stage(name) is None:
            stage = Stage(name)
            self.stages.append(stage)
            stages_db.insert(stage)
        return self.get_stage(name)

    def serialize(self):
        return {
            'stages': [stage.serialize() for stage in self.stages]
        }


class Step:
    """
    Represents a step in the pathway (a source together with the
    relevant input set).
    """

    @classmethod
    def load(self, serialized, context=None):
        source = sources_db.find(serialized['source_id'])
        input_set = InputSet(source.inputs(), context=context)
        values = serialized['user_inputs']
        if type(values) == dict:
            input_set = InputSet(source.inputs(), values)
        else:
            input_set.build(values)

        return Step(source, input_set)

    @classmethod
    def build(self, source_id, input_values=None, context=None):
        source = sources_db.find(source_id)
        if input_values is None:
            input_values = {}

        input_set = InputSet(source.inputs(), context=context)
        for input_name, input in input_set.inputs.items():
            if input.is_relevant(input_set):
                input_value = input_values.get(input_name)
                if input_value is not None:
                    input_set.set_value(input_name, input_value)
                else:
                    input_set.set_default(input_name)

        return Step(source, input_set)

    def __init__(self, source, input_set):
        self.source = source
        self.input_set = input_set

    @property
    def stage(self):
        return self.source.activity.stage

    @property
    def stage_name(self):
        return self.stage.name

    def serialize(self):
        return {
            'source_id': self.source.id,
            'user_inputs': self.input_set.values,
        }


class Pathway:

    @classmethod
    def load(cls, serialized, context=None):
        steps = [Step.load(item, context=context) for item in serialized['steps']]
        return Pathway(steps, name=serialized.get('name'))
    @classmethod
    def build(cls, items, context=None, **kwargs):
        def build_step(item):
            if type(item) == str:
                return Step.build(item, context=context)
            else:
                return Step.build(*item, context=context)

        steps = [build_step(item) for item in items]
        return Pathway(steps, **kwargs)

    def __init__(self, steps, name='Untitled', results=None):
        self.steps = steps
        self.name = name
        if name == 'Untitled':
            self.name = self.steps[2].source.cls.__name__
        self.results = results
        self.instances = {}

    def instance(self, stage_id):
        return self.instances.get(stage_id)

    def perform(self):
        for step in self.steps:
            obj = step.source.instantiate()
            obj.prepare(step.input_set)
            obj.pathway = self
            self.instances[step.stage.id] = obj

        results = {}
        prev_output = None

        for step in self.steps:
            obj = self.instances[step.stage.id]
            obj.output = prev_output
            obj.prepare(step.input_set)

            results[step.source.activity.stage] = obj
            prev_output = obj.get_inputs()['primary']

        self.results = {
            str(stage): obj.serialize() for stage, obj in results.items()
        }

        return self.results

    def sensitivity_analysis(self):
        return SensitivityAnalysis(self, compute_emissions)

    def serialize(self):
        return {
            'name': self.name,
            'steps': [step.serialize() for step in self.steps]
        }


class ActivitySource(DataSource, InputSource, Versioned):
    filters = []
    lookup_table = None

    _df = None

    @classmethod
    def sensitivity(cls):
        return None

    @classmethod
    def data_frame(cls):
        if cls._df is None:
            df = pd.read_csv(cls.lookup_table)

            for field, value in cls.filters:
                df = df[df[field] == value]

            cls._df = df
        return cls._df.copy()

    def __init__(self, output=None):
        self.output = output
        self.table = type(self).lookup_table
        self.user_inputs = []

    def get_output(self):
        return self.output

    def get_emissions(self):
        return {}

    def serialize(self):
        return {
            'user_inputs': self.input_values,
            'flow_inputs': self.get_inputs(),
            'flow_output': self.get_output(),
            'flow_emissions': self.get_emissions(),
        }
