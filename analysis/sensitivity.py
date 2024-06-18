from pprint import pprint

from core.inputs import InputSet

_cache = {}

class SensitivityInput:
    data_lacking_scalar = 0.3

    def __init__(self, name, minimizing=None, maximizing=None, data_lacking=False):
        self.name = name
        self._minimizing = minimizing
        self._maximizing = maximizing
        self.data_lacking = data_lacking

    def minimizing(self, input_set):
        if self._minimizing is not None:
            return self._minimizing

        if self.data_lacking:
            default_value = input_set.default_value(self.name)
            return (1 - self.data_lacking_scalar) * default_value

        raise ValueError(f'no minimizing value for input: {self.name}')

    def maximizing(self, input_set):
        if self._maximizing is not None:
            return self._maximizing

        if self.data_lacking:
            default_value = input_set.default_value(self.name)
            return (1 + self.data_lacking_scalar) * default_value

        raise ValueError(f'no maximizing value for input: {self.name}')


class SensitivityAnalysis:

    def __init__(self, pathway, runner, params=None):
        self.pathway = pathway
        self.runner = runner
        self.params = params or {}

        self.sensitivity_inputs = {}
        for step in self.pathway.steps:
            self.sensitivity_inputs[step.source] = [
                sensitivity_input
                for sensitivity_input in step.source.sensitivity(**self.params) or []
                if sensitivity_input.name in step.input_set
            ]

    @property
    def runnable(self):
        res = False
        for source, inputs in self.sensitivity_inputs.items():
            if len(inputs) > 0:
                res = True
                break
        return res

    def default_input_sets(self):
        return {
            source: InputSet.build_default(source)
            for source in self.sensitivity_inputs.keys()
        }

    def base_value(self):
        return self.runner(self.pathway, self.default_input_sets())

    def run(self, source, input_name, input_value):
        pathway_key = tuple([
            type(self.pathway).__module__,
            type(self.pathway).__name__,
        ] + [
            step.source.identifier()
            for step in self.pathway.steps
        ])

        cache_key = (
            pathway_key,
            type(source).__module__,
            type(source).__name__,
            source.identifier(),
            input_name,
            input_value,
        )

        if cache_key not in _cache:
            input_sets = self.default_input_sets()

            # make sure defaults are set properly
            values = { input_name: input_value }
            input_set = InputSet.build_default(source, values=values)
            input_sets[source] = input_set

            _cache[cache_key] = self.runner(self.pathway, input_sets)

        return _cache[cache_key]

    def serialize(self):
        default_input_sets = self.default_input_sets()
        return {
            'base_value': self.base_value(),
            'inputs': [
                self._serialize_input(source, input, default_input_sets)
                for source, inputs in self.sensitivity_inputs.items()
                for input in inputs
            ],
        }

    def _serialize_input(self, source, sensitivity_input, default_input_sets):
        input_set = default_input_sets[source]
        user_input = input_set.input(sensitivity_input.name)

        minimizing = sensitivity_input.minimizing(input_set)
        maximizing = sensitivity_input.maximizing(input_set)

        return {
            'name': sensitivity_input.name,
            'label': user_input.label,
            'default_value': input_set.value(sensitivity_input.name),
            'minimizing_value': minimizing,
            'maximizing_value': maximizing,
            'min_value': self.run(source, sensitivity_input.name, minimizing),
            'max_value': self.run(source, sensitivity_input.name, maximizing),
            'unit': user_input.unit,
            'data_lacking': sensitivity_input.data_lacking,
        }


if __name__ == '__main__':
    from core.pathway import Pathway
    import pathway.topology

    # solar_pathway = Pathway.build([
    #     'enduse-electricity-default',
    #     'gatetoenduse-transmission-literaturereview',
    #     'process-solarpowerproduction-default',
    #     'upstream-solar-default',
    # ])

    # sensitivity = solar_pathway.sensitivity_analysis()

    # print('Solar LCA:')
    # print(sensitivity.serialize())

    # # solar TEA

    # from core.tea import TeaPathway
    # from tea.topology import tea_registry

    # analysis = tea_registry.lookup_by_name('Solar')
    # pathway = TeaPathway(analysis)
    # sensitivity = pathway.sensitivity_analysis()

    # print('Solar TEA:')
    # print(sensitivity.serialize())

    wind_pathway = Pathway.build([
        'enduse-electricity-default',
        'gatetoenduse-transmission-literaturereview',
        'process-windpowerproduction-default',
        'upstream-wind-default',
    ])

    sensitivity = wind_pathway.sensitivity_analysis()

    print('Wind LCA:')
    pprint(sensitivity.serialize())
