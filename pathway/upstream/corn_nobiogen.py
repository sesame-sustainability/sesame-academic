from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows
from core import conditionals, validators


class CornNoBiogen(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput(
            'luc_model', 'LUC & Farming Model',
            defaults=[Default('GTAP (LUC) & ICF/USDA (farming)')],
            tooltip=Tooltip(
                'LUC (land use change) and corn farming models play a significant role in corn ethanol consequential LCA. However, no consensus has been reached in this area about what are the best LUC and farming models. For more detail, see in the 1.Corn cultiv.+other Conseq. tab in the original excel model in SESAME backend folder: pathway/process/corn ethanol folder. Corn ethanol pathway does not include biogenic carbon accounting due to the offset (carbon neutral) effect, to be consistent with the original excel model.',
                source='GTAP, ICF, EPA RFS2 Page 470',
                source_link='https://digitalcommons.unl.edu/cgi/viewcontent.cgi?referer=http://scholar.google.com/&httpsredir=1&article=2623&context=usdaarsfacpub; https://biotechnologyforbiofuels.biomedcentral.com/track/pdf/10.1186/s13068-017-0877-y',
        )
        )
        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            self.output
        )

        return {
            'primary': None,
            'secondary': [val for _, val in flow_dict.items()]
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            self.output
        )
