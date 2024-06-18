from core.pathway import ActivitySource


class Solar(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return []

    def get_inputs(self):
        return {
            'primary': None,
            'secondary': []
        }

    def get_emissions(self):
        emission_flows = {}
        for category in self.output:
            emission_flows[category] = {'co2': {'name': 'co2',
                                                'unit': 'gCO\u2082e/kWh',
                                                'value': self.output[category]}
                                        }
        return emission_flows
