from core.pathway import ActivitySource


class Wind(ActivitySource):

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
        multiplier = self.output['__multiplier']
        del self.output['__multiplier']

        for category in self.output:
            emission_flows[category] = {
                'co2': {
                    'name': 'co2',
                    'unit': 'kg',
                    'value': self.output[category]['lifetime'] * multiplier
                },
            }

        return emission_flows
