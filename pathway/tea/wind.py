from core.pathway import ActivitySource
from tea.electricity.wind.wind_tea import WindTEA

class Wind(ActivitySource):

    filters = [('Group By', 'State')]
    @classmethod
    def user_inputs(cls):
        return WindTEA.user_inputs(with_lca=True)

    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }
