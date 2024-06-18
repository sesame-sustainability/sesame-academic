from core.common import DataSource, InputSource, Versioned
from core.inputs import InputSet
import numbers
from pandas.api.types import is_numeric_dtype
import pandas as pd
from analysis.sensitivity import SensitivityAnalysis
import analysis.tea as tea

def pathway_id(pathway):
    activities = {}
    for step in pathway.steps:
        activities[step.stage_name] = step.source.activity

    return (
        activities['Enduse'].id,
        activities['Process'].id,
        activities['Upstream'].id
    )

def compute_cost(tea_pathway, input_sets):
    input_set = input_sets[tea_pathway.analysis]

    # instantiate a new pathway since the one passed in may have been
    # created with an `lca_pathway` present
    tea_pathway = TeaPathway(tea_pathway.analysis, input_set)

    results = tea.run(tea_pathway)
    cost = results['data']['value'].sum()
    return cost

class TeaBase(DataSource, InputSource, Versioned):
    unit = 'unknown'
    filters = []

    @classmethod
    def sensitivity(cls, *args, **kwargs):
        return None

    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        self.table = None
        self._df = None

    def prepare(self, input_set):
        if self.lca_pathway is not None:
            instance = self.lca_pathway.instance('tea')
            if instance is not None:
                # copy input values from pathway instance to this TEA instance
                for input in type(self).user_inputs(with_lca=True):
                    input_set.set_value(input.name, instance.input_value(input.name))
        super().prepare(input_set)

    def get_cost_breakdown(self):
        return {}

    def get_table(self):
        return None

class TeaAnalysis:

    def __init__(self, name, cls, pathway_id=None, table=None, conditionals=None):
        self.name = name
        self.cls = cls
        self.pathway_id = pathway_id
        self.table = table

        # if specified, these conditionals will be applied to every user input for this analysis
        self.conditionals = conditionals

    def __call__(self, *args, **kwargs):
        return self.instantiate(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def unit(self):
        return self.cls.unit

    def identifier(self):
        return self.name.lower().replace(' ', '')

    def instantiate(self, **kwargs):
        obj = self.cls(**kwargs)
        obj.table = self.table
        return obj

    def inputs(self):
        inputs = self.cls.user_inputs()
        if self.conditionals is not None:
            for input in inputs:
                input.conditionals += self.conditionals
        return inputs

    def sensitivity(self, *args, **kwargs):
        return self.cls.sensitivity(*args, **kwargs)

    def serialize(self):
        return {
            'name': self.name,
            'unit': self.unit,
            'pathway_id': self.pathway_id or ('placeholder', 'placeholder', 'placeholder'),
            'user_inputs': [
                input.serialize()
                for input in self.inputs()
            ],
            'version': self.cls.version,
        }

class ComposedAnalysis:

    class TeaBase:

        def __init__(self, parent):
            # `parent` is the instance of `ComposedAnalysis` that instantiated this
            self.parent = parent

            self.instances = {
                analysis: analysis.instantiate()
                for analysis in self.parent.analyses
            }

            for analysis in self.parent.analyses:
                setattr(self, analysis.name, self.instances[analysis])

        def prepare(self, input_set):
            for instance in self.instances.values():
                instance.prepare(input_set)

        def current_instance(self):
            # TODO: there's probably a more robust way to determine this
            for analysis in self.parent.analyses:
                instance_input_set = self.instances[analysis].input_set
                instance_inputs = list(instance_input_set.inputs.values())

                analysis_inputs = [
                    input
                    for input in analysis.inputs()
                    if input.is_relevant(instance_input_set)
                ]

                if len(instance_inputs) < len(analysis_inputs):
                    return self.instances[analysis]

            return list(self.instances.values())[-1]

        def categorical_options(self, input):
            return self.current_instance().categorical_options(input)

        def get_table(self):
            return None

    def __init__(self, name, pathway_id=None):
        self.name = name
        self.pathway_id = pathway_id
        self.analyses = type(self).analyses

    def __str__(self):
        return self.name

    def identifier(self):
        return self.name.lower().replace(' ', '')

    def instantiate(self):
        return type(self).TEA(self)

    def inputs(self):
        res = []
        for analysis in self.analyses:
            for input in analysis.inputs():
                input._source_analysis = analysis
                res.append(input)
        return res

    def serialize(self):
        return {
            'name': self.name,
            'pathway_id': self.pathway_id or ('placeholder', 'placeholder', 'placeholder'),
            'user_inputs': [
                input.serialize()
                for input in self.inputs()
            ]
        }


class TeaRegistry:

    def __init__(self):
        self._by_name = {}
        self._by_pathway_id = {}

    def lookup_by_name(self, name):
        return self._by_name[name]

    def lookup_by_pathway_id(self, pathway_id):
        return self._by_pathway_id[pathway_id]

    @property
    def analyses(self):
        return list(self._by_name.values())

    def register(self, analysis):
        self._by_name[analysis.name] = analysis
        if analysis.pathway_id is not None:
            if type(analysis.pathway_id) != list:
                if analysis.pathway_id in self._by_pathway_id:
                    raise Exception(f'duplicate pathway_id: ${analysis.pathway_id}')
                self._by_pathway_id[analysis.pathway_id] = analysis
            elif type(analysis.pathway_id) == list:
                for pid in analysis.pathway_id:
                    if pid in self._by_pathway_id:
                        raise Exception(f'duplicate pathway_id: ${pid}')
                    self._by_pathway_id[pid] = analysis

        return analysis

    def register_tea_analysis(self, name, cls, **kwargs):
        analysis = TeaAnalysis(name, cls, **kwargs)
        self.register(analysis)
        return analysis

    def serialize(self):
        return [
            analysis.serialize()
            for analysis in self.analyses
        ]

class TeaStep:

    def __init__(self, source, input_set):
        self.source = source
        self.input_set = input_set

class TeaPathway:

    @classmethod
    def load(cls, analysis, values):
        input_set = InputSet(analysis.inputs())
        input_set.build(values)
        return TeaPathway(analysis, input_set=input_set)

    def __init__(self, analysis, input_set=None, lca_pathway=None):
        self.analysis = analysis
        self.input_set = input_set or InputSet(self.analysis.inputs())
        self.lca_pathway = lca_pathway

    @property
    def name(self):
        return self.analysis.name

    @property
    def unit(self):
        return self.analysis.unit

    @property
    def steps(self):
        # to expose an interface similar to LCA pathways
        # (used in sensitivity analysis, for example)
        return [
            TeaStep(self.analysis, self.input_set)
        ]

    def sensitivity_analysis(self):
        return SensitivityAnalysis(self, compute_cost, params={'lca_pathway': self.lca_pathway })

    def perform(self):
        obj = self.analysis.instantiate(lca_pathway=self.lca_pathway)
        obj.prepare(self.input_set)

        return {
            'pathway_name': self.name,
            'cost_breakdown': obj.get_cost_breakdown(),
            'table': obj.get_table(),
        }
