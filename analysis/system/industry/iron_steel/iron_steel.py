import re

from core.common import InputSource, Versioned
from core.inputs import OptionsInput, InputSet
from core.model import ModelComposer

from analysis.system.industry.iron_steel.eaf import EAF
from analysis.system.industry.iron_steel.bf_bof import BFBOF
from analysis.system.industry.iron_steel.corex_bof import COREXBOF
from analysis.system.industry.iron_steel.hisarna_bof import HisarnaBOF
from analysis.system.industry.iron_steel.h_dri_eaf import HDRIEAF
from analysis.system.industry.iron_steel.ng_dri_eaf import NG_DRI_EAF
from analysis.system.industry.iron_steel.coal_dri import Coal_DRI

def prefix(route):
    return re.sub(r'[^A-Za-z0-9]+', '_', route).lower()

class IronSteel(InputSource, Versioned):
    routes = [
        ('Scrap-EAF (Scrap Based Electric Arc Furnace)', EAF),
        ('BF-BOF (Blast Furnace-Basic Oxygen Furnace)', BFBOF),
        ('Hisarna-BOF/SR_BOF (Hisarna-Basic Oxygen Furnace/Smelting Reduction-Basic Oxygen Furnace)', HisarnaBOF),
        ('H-DRI-EAF (Hydrogen Based Direct Reduction Iron-Electric Arc Furnace)', HDRIEAF),
        ('COREX-BOF (COREX-Basic Oxygen Furnace)', COREXBOF),
        ('NG-DRI-EAF (Natural Gas Based Direct Reduction Iron-Electric Arc Furnace)', NG_DRI_EAF),
        ('Coal-DRI-EAF(Coal Based Direct Reduction Iron-Electric Arc Furnace)', Coal_DRI)
    ]

    @classmethod
    def user_inputs(cls):
        inputs = [
            OptionsInput(
                'route', 'Iron or steel production method',
                options=[route for route, model in cls.routes],
            ),
        ]

        composer = ModelComposer(cls.routes, 'route')
        return inputs + composer.merged_inputs()

    def run(self):
        if self.route == 'BF-BOF (Blast Furnace-Basic Oxygen Furnace)':
            self.model = BFBOF()
        elif self.route == 'Scrap-EAF (Scrap Based Electric Arc Furnace)':
            self.model = EAF()
        elif self.route == 'Hisarna-BOF/SR_BOF (Hisarna-Basic Oxygen Furnace/Smelting Reduction-Basic Oxygen Furnace)':
            self.model = HisarnaBOF()
        elif self.route == 'H-DRI-EAF (Hydrogen Based Direct Reduction Iron-Electric Arc Furnace)':
            self.model = HDRIEAF()
        elif self.route == 'COREX-BOF (COREX-Basic Oxygen Furnace)':
            self.model = COREXBOF()
        elif self.route == 'NG-DRI-EAF (Natural Gas Based Direct Reduction Iron-Electric Arc Furnace)':
            self.model = NG_DRI_EAF()
        elif self.route == 'Coal-DRI-EAF(Coal Based Direct Reduction Iron-Electric Arc Furnace)':
            self.model = Coal_DRI()
        else:
            raise Exception(f'invalid route: {self.route}')

        composer = ModelComposer(self.routes, 'route')
        composer.prepare(self.input_set, self.model)

        return self.model.run()

    def figures(self, results):
        return self.model.figures(results)

    def plot(self, results):
        return self.model.plot(results)
