from core.pathway import ActivitySource
from core.inputs import CategoricalInput, Default
from analysis.lca import compute_input_flows, compute_emission_flows


class NGPowerGREET(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            # OptionsInput('user_effeciency','Use user-specified effeciency?', options=['Yes','No']),
            # ContinuousInput('efficiency', 'Power Generation Efficiency (%), between 28 and 55 recommended',
            #                 validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            #                 conditionals=[conditionals.input_equal_to('user_effeciency','Yes')]),
            CategoricalInput('generation_region', 'Generation Region', defaults=[Default('US')]),
            CategoricalInput('generator_type', 'Generator Type', defaults=[Default('Mix')]),
            CategoricalInput('infrastructure_emission_inclusion', 'Include Infrastructure Emissions?', defaults=[Default('Yes')])
        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
        return {
            'primary': flow_dict['natural gas'],
            'secondary': []
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
