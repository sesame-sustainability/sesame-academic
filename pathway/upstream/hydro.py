from core.pathway import ActivitySource


class Hydro(ActivitySource):

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
        emission_flows['aggregate'] = {'co2': {'name': 'co2',
                                                'unit': 'kg',
                                                'value': 0}
                                        }
        return emission_flows
