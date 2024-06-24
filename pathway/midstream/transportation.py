import os

import pandas as pd

from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows
import core.conditionals as conditionals
import core.validators as validators
from analysis.sensitivity import SensitivityInput

DATA = {
    'loss_defaults': pd.read_csv(os.path.join(os.getcwd(), 'pathway', 'midstream', 'loss_defaults.csv')),
}


class Transportation(ActivitySource):

    @classmethod
    def user_inputs(cls, default_mode, feed):
        df = cls.data_frame()
        df['Distance'] = df['Default Distance (mile one-way)']
        df = df[['Transport Mode, Upstream to Process', 'Distance']].drop_duplicates()

        default_distances = [
            Default(
                row['Distance'],
                conditionals=[conditionals.input_equal_to('mode', row['Transport Mode, Upstream to Process'])]
            )
            for _, row in df.iterrows()
        ]

        loss_df = DATA['loss_defaults']
        default_loss = loss_df[loss_df['Feed'] == feed]["Default Loss in %"].iloc[0]

        return [
            CategoricalInput(
                'mode', 'Transport Mode, Upstream to Process',
                defaults=[Default(default_mode)],
                tooltip=Tooltip(
                    ' ',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                )

            ),
            ContinuousInput(
                'distance', 'Distance, Upstream to Process',
                unit='mi',
                defaults=default_distances,
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    ' ',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                )

            ),
            ContinuousInput(
                'loss_factor', 'Loss, Upstream to Process',
                unit='%',
                defaults=[Default(default_loss)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                tooltip=Tooltip(
                    ' ',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                )

            ),
        ]

    @classmethod
    def sensitivity(cls):
        return [SensitivityInput('distance', data_lacking=True), SensitivityInput('loss_factor',data_lacking=True)]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output,
            flow_info={'distance': self.distance}
        )

        primary = self.output.copy()
        primary['value'] = self.output['value'] / (1 - 0.01 * self.loss_factor)

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


class CoalTransportation(Transportation):
    filters = [
        ('Feed', 'coal'),
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("Default Mix", "coal")

    @property
    def coal_type(self):
        if not hasattr(self, 'pathway'):
            return None

        return self.pathway.instance('upstream').coal_type

    def filtered_data_frame(self):
        df = super().filtered_data_frame()
        if self.coal_type:
            df = df[df['Sub Feed'] == self.coal_type]
        return df


class NGElectricityTransportation(Transportation):
    filters = [
        ('Feed', 'natural gas')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("Pipeline", "ng electricity")


class NGNonElectricityTransportation(Transportation):
    filters = [
        ('Feed', 'natural gas')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("Pipeline", "ng non-electricity")


class CrudeTransportation(Transportation):
    filters = [
        ('Feed', 'crude')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "crude")


class UraniumTransportation(Transportation):
    filters = [
        ('Feed', 'uranium')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("truck", "uranium")

class CornTransportation(Transportation):
    filters = [
        ('Feed', 'corn')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "corn")

class StoverTransportation(Transportation):
    filters = [
        ('Feed', 'corn stover')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("truck", "corn stover")

class ConcreteTransportation(Transportation):
    filters = [
        ('Feed', 'concrete feeds (49% gravel/35% sand/9% cement/7% water)')
    ]

    @classmethod
    def user_inputs(cls):
        return super().user_inputs("default mix", "concrete feeds (49% gravel/35% sand/9% cement/7% water)")
