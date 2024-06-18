import core.analysis as analysis
from core.inputs import InputSet
from core.pathway import Pathway, sources_db
import core.tea as tea
from schematics.exceptions import ValidationError, BaseError
from schematics.models import Model
from schematics.types import StringType, IntType, FloatType, ListType, ModelType, UnionType, DictType, BaseType
from tea.topology import tea_registry

class Auth(Model):
    email = StringType(required=True)
    password = StringType(required=True)

class StepModel(Model):
    source_id = StringType(required=True)
    user_inputs = ListType(UnionType((IntType, FloatType, StringType)))

class PathwayModel(Model):
    name = StringType()
    steps = ListType(ModelType(StepModel), required=True, min_size=1)

class LcaAnalysis(Model):
    pathways = ListType(ModelType(PathwayModel), min_size=1)
    indicator = StringType(default='GWP')
    context = DictType(BaseType, default={
        'compute_cost': False,
    })

    def validate_pathways(self, data, values):
        for pathway in data['pathways']:
            for step in pathway.steps:
                source = sources_db.find(step.source_id)
                input_set = InputSet(source.inputs(), context=data['context'])
                input_set.build(step.user_inputs)
                try:
                    input_set.validate()
                except BaseError as e:
                    # we lose the context of which pathway+step this is part of,
                    # can we add that to the error?
                    raise e

class TeaAnalysis(Model):
    analysis_name = StringType()
    user_inputs = ListType(UnionType((IntType, FloatType, StringType)))
    pathway = ModelType(PathwayModel)

    def validate_user_inputs(self, data, values):
        if data['analysis_name'] is not None:
            tea_analysis = self._tea_analysis(data, values)
            input_set = InputSet(tea_analysis.inputs())
            input_set.build(values)
            input_set.validate()

    def validate_analysis_name(self, data, values):
        analysis = self._tea_analysis(data, values)
        if analysis is None:
            raise ValidationError('must provide analyis_name or pathway')

    def _tea_analysis(self, data, values):
        analysis_name = data['analysis_name']
        pathway = data['pathway']
        if analysis_name is not None:
            return tea_registry.lookup_by_name(analysis_name)
        elif pathway is not None:
            pathway = Pathway.load(pathway, context={ 'compute_cost': True })
            pathway_id = tea.pathway_id(pathway)
            return tea_registry.lookup_by_pathway_id(pathway_id)
