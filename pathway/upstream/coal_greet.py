from core import validators
from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows


class CoalGreet(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            OptionsInput(
                'coal_type', 'Coal Type',
                options=[
                    'Bituminous',
                    'Lignite',
                    'Mix (~50% Bituminous, 40% Sub-bituminous, 5% Lignite, 5% Other)',
                    'Subbituminous',
                ],
                defaults=[Default('Mix (~50% Bituminous, 40% Sub-bituminous, 5% Lignite, 5% Other)')],
                tooltip=Tooltip(
                    'Different types of coals vary in carbon and energy content, which impacts emissions during combustion for power generation. US average mix is used as default. Note that emissions in the upstream extraction do not depend on the specific coal types, mainly due to lack of emissions data per coal type, and the fact that most GHG emissions for coal power originates from the power plant. An average mix is assumed for the upstream.',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                )

            ),
            ContinuousInput(
                'underground_share', 'Share of Coal from Underground Mining (%)',
                defaults=[Default(31)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                tooltip=Tooltip(
                    'Coal mining method/location impacts upstream emissions.',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                )

            ),
            CategoricalInput(
                'well_infrastructure',
                'Count Emissions from Building Extraction Infrastructure',
                defaults=[Default('Yes')],
                tooltip=Tooltip(
                    'Emissions associated with the cement, steel, etc. used for constructing the mining infrastructure, amortized over the plant lifetime and levelized by plant power output. This contribution to LCA is very small and thus often ignored by many LCA studies.',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                )

            ),
        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(self._get_df(), self.output)
        return {
            'primary': None,
            'secondary': [val for _, val in flow_dict.items()]
        }

    def get_emissions(self):
        return compute_emission_flows(self._get_df(), self.output)

    def _get_df(self):
        df = self.filtered_data_frame()
        # aggregates underground and surface emissions by underground mining share
        surface_underground = df[df["method"].isin(["Underground", "Surface"])]
        combined_df = df[~df["method"].isin(["Underground", "Surface"])]

        for flow in surface_underground.flows.unique():
            underground_row = surface_underground[(surface_underground.method == "Underground") &
                                                  (surface_underground.flows == flow)].iloc[0]
            surface_row = surface_underground[(surface_underground.method == "Surface") &
                                              (surface_underground.flows == flow)].iloc[0]
            underground_row['value'] = (underground_row['value'] * self.underground_share / 100.0 +
                                        surface_row['value'] * (100 - self.underground_share) / 100.0)
            combined_df = combined_df.append(underground_row, ignore_index=True)
        combined_df = combined_df.drop(columns=['method'])
        return combined_df
