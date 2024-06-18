from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows
from core import conditionals, validators


class StoverWithBiogen(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('farm_management_corn_only)', 'Farm Management Scenario (Corn Only)',
            defaults=[Default('NRR/CON')],
            tooltip=Tooltip(
                'Biofuels require consequential LCA using system expansion method, i.e., comparing System 1 where farmers only grow and sell corn and System 2 where farmers sell both corn and corn stover. Different farming practices are included here. NRR: No Residue Removal; MRR: Moderate Residue Removal; HRR: High Residue Removal; CON: Conventional Tillage; ALT: Alternative Tillage. For more details, see the JCP paper linked, or the 1. Crop Cultivation tab in the original excel model in SESAME backend folder: pathway/process/corn stover ethanol folder.',
                source='JCP paper',
                source_link='https://www.sciencedirect.com/science/article/pii/S0959652619308455',
            )
        ),

            CategoricalInput('farm_management_corn_and_stover)', 'Farm Management Scenario (Corn & Stover)',
            defaults=[Default('MRR/ALT')],
                     tooltip = Tooltip(
            'Biofuels require consequential LCA using system expansion method, i.e., comparing System 1 where farmers only grow and sell corn and System 2 where farmers sell both corn and corn stover. Different farming practices are included here. NRR: No Residue Removal; MRR: Moderate Residue Removal; HRR: High Residue Removal; CON: Conventional Tillage; ALT: Alternative Tillage. For more details, see the JCP paper linked, or the 1. Crop Cultivation tab in the original excel model in SESAME backend folder: pathway/process/corn stover ethanol folder. LUC (land use change) model used: FASOM (EPA RFS2, Page 470). GCAM LUC model gives similar result. Corn stover ethanol pathway includes biogenic carbon accounting, to be consistent with the original excel model.',
            source='JCP paper',
            source_link='https://www.sciencedirect.com/science/article/pii/S0959652619308455',
                     )
        ),
            CategoricalInput('harvesting_method', 'Harvesting Method',
            defaults=[Default('single pass')],
                     tooltip = Tooltip(
            'Whether the stovers are harvested in one or two passes by truck on the farm. Single pass is based on expert view.',
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
