import os

import pandas as pd

from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from core import validators, conditionals
from analysis.lca import compute_input_flows, compute_emission_flows
from analysis.sensitivity import SensitivityInput


class Transportation(ActivitySource):

    @classmethod
    def user_inputs(cls, default_mode, product):
        df = cls.data_frame()
        df['Distance'] = df['Default Distance (mile one-way)']
        df = df[['Transport Mode, Process to Use', 'Distance']].drop_duplicates()

        default_distances = [
            Default(
                row['Distance'],
                conditionals=[
                    conditionals.input_equal_to('mode', row["Transport Mode, Process to Use"])
                ]
            )
            for _, row in df.iterrows()
        ]

        loss_df = pd.read_csv(os.getcwd() + "/pathway/gate_to_enduse/loss_defaults.csv")
        default_loss = loss_df[loss_df['Product'] == product]["Default Loss in %"].iloc[0]

        return [
            CategoricalInput('mode', 'Transport Mode, Process to Use', defaults=[Default(default_mode)],
                             tooltip=Tooltip(
                                 ' ',
                                 source='GREET2019',
                                 source_link='https://greet.es.anl.gov/',
                             )
                             ),
            ContinuousInput('distance', 'Distance, Process to Use (mi)', defaults=default_distances,
                            validators=[validators.numeric(), validators.gte(0)],
                            tooltip=Tooltip(
                                ' ',
                                source='GREET2019',
                                source_link='https://greet.es.anl.gov/',
                            )
                            ),
            ContinuousInput('loss', 'Loss, Process to Use (%)', defaults=[Default(default_loss)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            tooltip=Tooltip(
                                ' ',
                                source='GREET2019',
                                source_link='https://greet.es.anl.gov/',
                            )
                            )
        ]

    @classmethod
    def sensitivity(cls):
        return [SensitivityInput('distance', data_lacking=True), SensitivityInput('loss', data_lacking=True)]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            self.output,
            {'distance': self.distance}
        )

        primary = self.output.copy()
        primary['value'] = self.output['value'] / (1 - 0.01 * self.loss)

        return {
            'primary': primary,
            'secondary': [val for _, val in flow_dict.items()]
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            self.output,
            {'distance': self.distance}
        )


class GasolineTransportation(Transportation):
    filters = [
        ('Feed', 'gasoline')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("truck", "gasoline")


class DieselTransportation(Transportation):
    filters = [
        ('Feed', 'diesel')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "diesel")

class EthanolTransportationNoBiogen(Transportation):
    filters = [
        ('Feed', 'ethanol')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "ethanol")

class EthanolTransportationWithBiogen(Transportation):
    filters = [
        ('Feed', 'ethanol')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "ethanol")

class LPGTransportation(Transportation):
    filters = [
        ('Feed', 'lpg')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "lpg")


class LNGTransportation(Transportation):
    filters = [
        ('Feed', 'lng')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "lng")


class MethanolTransportation(Transportation):
    filters = [
        ('Feed', 'meoh')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "meoh")


class DMETransportation(Transportation):
    filters = [
        ('Feed', 'dme')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "dme")


class HydrogenGasTransportation(Transportation):
    filters = [
        ('Feed', 'h2 gas')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "h2 gas")


class HydrogenLiquidTransportation(Transportation):
    filters = [
        ('Feed', 'h2 liquid')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "h2 liquid")


class JetFuelTransportation(Transportation):
    filters = [
        ('Feed', 'jet fuel')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "jet fuel")


class EthanolTransportation(Transportation):
    filters = [
        ('Feed', 'etoh')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "etoh")


class AmmoniaTransportation(Transportation):
    filters = [
        ('Feed', 'ammonia')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "ammonia")


class UreaTransportation(Transportation):
    filters = [
        ('Feed', 'urea')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "urea")


class ConcreteTransportation(Transportation):
    filters = [
        ('Feed', 'concrete')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("truck", "concrete")


class IronTransportation(Transportation):
    filters = [
        ('Feed', "iron (using GREET cement data as dummy)")
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("mix of truck barge & rail", "iron (using GREET cement data as dummy)")


class CementTransportation(Transportation):
    filters = [
        ('Feed', 'cement')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("mix of truck barge & rail", "cement")


class SteelTransportation(Transportation):
    filters = [
        ('Feed', "steel (using GREET concrete data as dummy)")
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("truck", "steel (using GREET concrete data as dummy)")


class JetFuelTransportation(Transportation):
    filters = [
        ('Feed', 'jet fuel')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "jet fuel")