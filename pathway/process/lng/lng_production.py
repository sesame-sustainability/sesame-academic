from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows


class LNGProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('leakage_param', 'Methane Fugitive Parameter',
                     defaults=[Default('EPA 2019')],
                     tooltip=Tooltip(
                        'Unlike the other pathways, LNG pathway LCA does not include LNG end use emissions, due to variations of how it can finally be used. E.g., if it will be burned, then the combustion emission of 57 g CO2/MJ LHV LNG should be added.',
                         source='GREET2019',
                         source_link='https://greet.es.anl.gov/',
        )
        )
        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        return {
            'primary': flow_dict['natural gas'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'natural gas']
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
