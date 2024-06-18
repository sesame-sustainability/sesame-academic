from core.pathway import ActivitySource
from core.inputs import CategoricalInput
from analysis.lca import compute_input_flows, compute_emission_flows
import pandas as pd


class GasolineProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
        ]
#                tooltip=Tooltip(
#                    'Caveat: GREET does not have crude-specific refining emission models built in, and thus we are using an average refining emissions here, which does not change with the crude type. However, by varying the available crude sulfur content and API knobs in GREET, we found that such variation does not have a very large impact on the refining emissions and even smaller impact on well-to-wheel LCA because the lifecycle GHG emissions are dominated by end-use combustion. The impact is a few percent deviation (lifecycle-wise) from the base case when compared with the extreme cases of sulfur content and API (thus refining efficiency) in GREET',
#                    source='GREET2019',
#                    source_link='https://greet.es.anl.gov/',


    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        return {
            'primary': flow_dict['petroleum'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'petroleum']
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
