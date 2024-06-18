import re

from core.common import InputSource, Versioned
from core.inputs import OptionsInput, InputSet, Default,Tooltip
from core.model import ModelComposer

from analysis.system.industry.aluminum.bayer_hall_heroult import BAYERHALLHEROULT
from analysis.system.industry.aluminum.remelt_aluminum import REMELTALUMINUM
from analysis.system.industry.aluminum.recycle_aluminum import RECYCLEALUMINUM

def prefix(route):
    return re.sub(r'[^A-Za-z0-9]+', '_', route).lower()

class Aluminum(InputSource, Versioned):
    routes = [
        ('Primary Aluminum', BAYERHALLHEROULT),
        ('Remelt Aluminum', REMELTALUMINUM),
        ('Recycle Aluminum', RECYCLEALUMINUM),
    ]

    @classmethod
    def user_inputs(cls):
        inputs = [
            OptionsInput(
                'route', 'Aluminum production route',
                options=[route for route, model in cls.routes],
                defaults=[Default('Primary Aluminum')],
                tooltip=Tooltip(
                    'Primary Pathway Defaults based on literature',
                    source='European Aluminium Industry',
                    source_link='https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf')
            ),
        ]

        composer = ModelComposer(cls.routes, 'route')
        return inputs + composer.merged_inputs()

    def run(self):
        if self.route == 'Primary Aluminum':
            self.model = BAYERHALLHEROULT()
        elif self.route == 'Remelt Aluminum':
            self.model = REMELTALUMINUM()
        elif self.route == 'Recycle Aluminum':
            self.model = RECYCLEALUMINUM()
        else:
            raise Exception(f'invalid route: {self.route}')

        composer = ModelComposer(self.routes, 'route')
        composer.prepare(self.input_set, self.model)

        return self.model.run()

    def figures(self, results):
        return self.model.figures(results)

    def plot(self, results):
        return self.model.plot(results)
