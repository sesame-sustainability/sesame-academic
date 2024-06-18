from core.pathway import ActivitySource
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default
import core.conditionals as conditionals
import core.validators as validators
import pandas as pd
import os
from analysis.sensitivity import SensitivityInput


PARAMs = [{'name': 'Distance to grid of onshore wind farm, assumed', 'value': 20, 'unit': 'km'},
          {'name': 'Distance to grid of offshore wind farm, assumed', 'value': 72, 'unit': 'km'},
          {'name': 'Amount by which tower & foundation GHGs increase for every 1 meter increase in hub height',
           'value': 0.028, 'unit': '%/m'},
          {'name': 'Foreground upstream electricity contribution to total GHGs, reference', 'value': 0.38, 'unit': ''},
          {'name': 'GHG emissions intensity for upstream electricity, reference', 'value': 510, 'unit': 'g/kWh'},
          {'name': 'Transport share of GHGs, reference', 'value': 0.12, 'unit': ''},
          {'name': 'Material share of GHGs, reference', 'value': 0.64, 'unit': ''},
          {'name': 'Wind farm losses', 'value': 0.0835, 'unit': ''},
          {'name': 'Curtailment & availability losses', 'value': 0.03, 'unit': ''},
          {'name': 'Shear coefficient', 'value': 0.14, 'unit': ''}]

STEP_TO_COLUMN = {'operation': 'operation',
                  'installation': 'installation',
                  'foundation': 'foundation prod. (incl. substructure if offshore)',
                  'tower': 'tower prod.',
                  'hub': 'hub prod. ',
                  'nacelle': 'nacelle prod. (incl. generator, gear, shaft)',
                  'blade': 'blades prod.',
                  'cable': 'cables prod.',
                  'manufacturing': 'manufacturing',
                  'eol': 'EOL',
                  'avoided': 'total (avoided burden)',
                  'others': 'other GHGs',

                  }
REFERENCE_TABLE = pd.read_csv(os.getcwd() + "/pathway/process/wind/wind_reference_table.csv")


class WindPowerProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput(
                'install_type', 'Installation Type',
                defaults=[Default('onshore wind farm > 50MW')],
            ),
            OptionsInput(
                'choice', 'Choose Capacity Factor or Wind Speed',
                options=['Capacity Factor', 'Wind Speed'],
                defaults=[Default('Wind Speed')],
            ),
            CategoricalInput(
                'wind_speed', 'Average Wind Speed',
                conditionals=[conditionals.input_equal_to('choice', 'Wind Speed')],
                defaults=[Default('medium (8 m/s)')]
            ),
            OptionsInput(
                'cap_fac', 'Capacity Factor', unit='%',
                options=[20, 25, 30, 35, 40, 45, 50],
                conditionals=[conditionals.input_equal_to('choice', 'Capacity Factor')],
            ),
            OptionsInput(
                'hub_height', 'Hub Height', unit='m',
                options=[70, 80, 90, 100, 110, 120],
                defaults=[Default(100)],
            ),
            CategoricalInput(
                'years', 'Year Installed',
                defaults=[Default('2014-2016')],
            ),
            CategoricalInput(
                'turbine_model', 'Turbine Model',
                defaults=[
                    Default('Typical Onshore lo-spd', conditionals=[conditionals.input_equal_to('wind_speed', 'lowest (6 m/s)')]),
                    Default('Typical Onshore hi-spd', conditionals=[conditionals.input_equal_to('wind_speed', 'high (9 m/s)')]),
                    Default('Typical Onshore md-spd'),
                ],
            ),
            OptionsInput(
                'lifetime', 'Lifetime', unit='years',
                options=[5, 10, 20, 30, 40],
                defaults=[Default(20)],
            ),
            OptionsInput(
                'carbon_intensity', 'Emissions in Manufacturing', unit='gCO₂e/kWh',
                options=[50, 100, 200, 400, 600, 800, 1000],
                defaults=[Default(600)],
            ),
        ]

    @classmethod
    def sensitivity(cls):
        return [
            SensitivityInput(
                'install_type',
                minimizing='onshore wind farm > 50MW',
                maximizing='offshore wind farm > 50MW',
            ),
            SensitivityInput(
                'wind_speed',
                minimizing='high (9 m/s)',
                maximizing='lowest (6 m/s)',
            ),
            SensitivityInput(
                'hub_height',
                minimizing=80,
                maximizing=110,
            ),
            SensitivityInput(
                'turbine_model',
                minimizing='Vestas 112-3',
                maximizing='Vestas 100-2 (MC)',
            ),
            SensitivityInput(
                'lifetime',
                minimizing=30,
                maximizing=10,
            ),
            SensitivityInput(
                'carbon_intensity',
                minimizing=200,
                maximizing=1000,
            ),
        ]

    def get_inputs(self):
        if not hasattr(self,'results_wind'):
            self.results_wind = self.get_all_emissions()

        upstream_emissions = {
            key: val
            for key, val in self.results_wind.items()
            if (key != 'operation' and key != 'avoided' and key!= 'manufacturing')
        }

        multiplier = self.output['value']

        # FIXME
        # we're passing this multiplier, which indirectly represents the transmission loss
        # through to the upstream stage in this pathway
        upstream_emissions['__multiplier'] = multiplier

        return {
            'primary': upstream_emissions,
            'secondary': []
        }

    def get_output(self):
        return self.output

    def get_emissions(self):
        multiplier = self.output['value']
        emissions = self.results_wind

        return {
            'operation': {
                'co2': {
                    'name': 'co2',
                    'unit': 'kg',
                    'value': emissions['operation']['lifetime'] * multiplier
                },
            },
        }

    def get_upstream_elec(self, ref_ghg_op):
        return ref_ghg_op * (1 + (self.carbon_intensity / PARAMs[4]['value'] - 1) * PARAMs[3]['value'])/1000

    def get_distance_to_grid(self, upstream_elec, data, step):
        if step == 'cable':
            if self.install_type == 'onshore wind farm > 50MW':
                return upstream_elec * (PARAMs[0]['value'] / float(data['LCA reference distance to grid (km)']))
            else:
                return upstream_elec * (PARAMs[1]['value'] / float(data['LCA reference distance to grid (km)']))
        else:
            return upstream_elec

    def get_hub_height(self, distance_to_grid, data, step):
        constant = 0
        if step == "operation" or step == "installation":
            constant = 0.5
        elif step == "foundation":
            constant = 0.75
        elif step == "tower":
            constant = 1
        height_diff = self.hub_height - data['LCA reference tower height (m)']
        return distance_to_grid * (1 + constant * PARAMs[2]['value'] * height_diff)

    def get_user_cap(self, cap_fac, hub_height, data):
        return hub_height * (data['LCA reference CF'] / cap_fac) * 100

    def get_lifetime(self, user_cf, data):
        return user_cf * (data['LCA reference lifetime (years)'] / self.lifetime)

    def get_ghg_dict(self, elec, distance, height, cf, lifetime):
        ghg_dict = {"upstream_elec": elec,
                    "distance_to_grid": distance,
                    "hub_height": height,
                    "user_cf": cf,
                    "lifetime": lifetime
                    }
        return ghg_dict

    def compute_base_step_emission(self, ref_ghg_op, cap_fac, data, step):
        upstream_elec = self.get_upstream_elec(ref_ghg_op)
        distance_to_grid = self.get_distance_to_grid(upstream_elec, data, step)
        hub_height = self.get_hub_height(distance_to_grid, data, step)
        user_cf = self.get_user_cap(cap_fac, hub_height, data)
        lifetime = self.get_lifetime(user_cf, data)
        return self.get_ghg_dict(upstream_elec, distance_to_grid, hub_height, user_cf, lifetime)

    def compute_aggregate_step_emission(self, ref_ghg_op, cap_fac, data, step):

        installation = self.compute_base_step_emission(float(data[STEP_TO_COLUMN['installation']]), cap_fac, data, "installation")
        operation = self.compute_base_step_emission(float(data[STEP_TO_COLUMN['operation']]), cap_fac, data, "operation")
        foundation_prod = self.compute_base_step_emission(float(data[STEP_TO_COLUMN['foundation']]), cap_fac, data, "foundation")
        tower_prod = self.compute_base_step_emission(float(data[STEP_TO_COLUMN['tower']]), cap_fac, data, "tower")
        nacelle_prod = self.compute_base_step_emission(float(data[STEP_TO_COLUMN['nacelle']]), cap_fac, data, "nacelle")
        blade_prod = self.compute_base_step_emission(float(data[STEP_TO_COLUMN['blade']]), cap_fac, data, "blade")
        hub_prod = self.compute_base_step_emission(float(data[STEP_TO_COLUMN['hub']]), cap_fac, data, "hub")
        cable_prod = self.compute_base_step_emission(float(data[STEP_TO_COLUMN['cable']]), cap_fac, data, "cable")

        upstream_elec = self.get_upstream_elec(ref_ghg_op)

        if step == "manufacturing":
            distance_to_grid = upstream_elec + cable_prod['distance_to_grid'] - cable_prod['upstream_elec']
            hub_height = distance_to_grid - foundation_prod['distance_to_grid'] + foundation_prod['hub_height'] - tower_prod['distance_to_grid'] + tower_prod['hub_height']

        elif step == "avoided":
            manufacturing = self.compute_aggregate_step_emission(float(data[STEP_TO_COLUMN['manufacturing']]), cap_fac, data, 'manufacturing')
            upstream_elec = upstream_elec * data['total (avoided burden)']
            distance_to_grid = installation['distance_to_grid'] + operation['distance_to_grid'] + manufacturing['distance_to_grid']
            hub_height = installation['hub_height'] + operation['hub_height'] + manufacturing['hub_height']

        elif step == "eol":
            distance_to_grid = upstream_elec - 0.2*(cable_prod['distance_to_grid'] - cable_prod['upstream_elec'])
            hub_height = distance_to_grid * (1 + 0.7 * PARAMs[2]['value'] * (self.hub_height - data['LCA reference tower height (m)']))

        elif step == "others":
            avoided = self.compute_aggregate_step_emission(float(data[STEP_TO_COLUMN['avoided']]), cap_fac, data, 'avoided')
            distance_to_grid = upstream_elec
            hub_height = avoided['hub_height'] - (installation['hub_height'] + operation['hub_height'] + blade_prod['hub_height'] + cable_prod['hub_height'] + hub_prod['hub_height'] + tower_prod['hub_height'] + nacelle_prod['hub_height'] + foundation_prod['hub_height'])

        user_cf = self.get_user_cap(cap_fac, hub_height, data)
        lifetime = self.get_lifetime(user_cf, data)

        return self.get_ghg_dict(upstream_elec, distance_to_grid, hub_height, user_cf, lifetime)

    def get_all_emissions(self):
        data = REFERENCE_TABLE[REFERENCE_TABLE['Turbine Model'] == self.turbine_model].iloc[0]
        base_steps = ['operation', 'installation', 'foundation', 'tower', 'hub', 'nacelle', 'blade', 'cable']
        aggregate_steps = ['manufacturing', 'avoided', 'eol', 'others']

        ghg = {}
        all_steps = set(base_steps) | set(aggregate_steps)
        for step in all_steps:
            ref_ghg_op = float(data[STEP_TO_COLUMN[step]])
            cap_fac = data[self.wind_speed] if self.choice == "Wind Speed" else self.cap_fac
            if step in base_steps:
                ghg[step] = self.compute_base_step_emission(ref_ghg_op, cap_fac, data, step)
            if step in aggregate_steps:
                ghg[step] = self.compute_aggregate_step_emission(ref_ghg_op, cap_fac, data, step)

        return ghg

    def get_capacity_factor(self):
        data = REFERENCE_TABLE[REFERENCE_TABLE['Turbine Model'] == self.turbine_model].iloc[0]
        return data[self.wind_speed] if self.choice == "Wind Speed" else self.cap_fac
