import analysis.lca as lca_analysis
import analysis.tea as tea_analysis
from core.pathway import Step, Pathway
from core.inputs import CategoricalInput, OptionsInput, InputSet
import argparse
from core import graph
import json
import matplotlib.pyplot as plt

import core.tea as tea
from core.tea import TeaPathway

from pathway.topology import metadata as pathway_metadata
from tea.topology import tea_registry

import analysis.system.fleet.fleet as fleet
import analysis.system.grid.grid as grid
import analysis.system.industry.cement.cement as cement
import analysis.system.industry.iron_steel.iron_steel as iron_steel
import analysis.system.industry.aluminum.aluminum as aluminum
import analysis.system.industrial_fleet.industrial_fleet as industrial_fleet
import analysis.system.pps.power_plus_storage as pps

def prompt_options(options, label):
    try:
        for i in range(len(options)):
            print(f'{i + 1}: {options[i]}')
        inp = int(input(f'{label}: '))
        while inp not in range(1, len(options) + 1):
            print('Please select an input from options above!')
            inp = int(input(f'Choose {label} from options above: '))
        return options[inp - 1]
    except TypeError:
        print('Input value must be numeric')

def prompt_value(user_input, input_set):
    try:
        label = f'{user_input.label}'
        if user_input.unit:
            label = f'{label} ({user_input.unit})'
        default = input_set.default_value(user_input.name)
        if default:
            label = f'{label} [default={default}]'
        label = f'{label}: '

        val = input(label)
        if val == '':
            val = default

        return float(val)
    except ValueError:
        print('Input value must be numeric')

def prompt_input(user_input, input_set, source=None):
    if user_input.input_type == 'categorical':
        obj = source.instantiate()
        obj.prepare(input_set)
        options = obj.categorical_options(user_input)
        return prompt_options(options, user_input.label)
    elif user_input.input_type == 'options':
        return prompt_options([
            option.value
            for option in user_input.options
            if option.is_relevant(input_set)
        ], user_input.label)
    else:
        return prompt_value(user_input, input_set)

def prompt_inputs(inputs=None, input_set=None, source=None, context=None):
    if inputs is None:
        if source is None:
            raise Exception('must provide `inputs` or `source`')
        inputs = source.inputs()

    if input_set is None:
        input_set = InputSet(inputs, context=context)

    for input in inputs:
        if input.input_type == 'group':
            print('---')
            print(input.label)
            print('---')
        else:
            if input.is_relevant(input_set):
                value = prompt_input(input, input_set, source=source)
                input_set.set_value(input.name, value)

        prompt_inputs(inputs=input.children.copy(), input_set=input_set, source=source)

    return input_set

class CLI:

    def __init__(self, args):
        self.args = args
        self.context = {}

    def inputs(self):
        return []

    def prompt_inputs(self):
        kwargs = {}
        if self.source:
            kwargs['source'] = self.source
        else:
            kwargs['inputs'] = self.inputs()

        if self.args.defaults:
            self.input_set = InputSet.build_default(self.source, context=self.context)
        else:
            self.input_set = prompt_inputs(**kwargs)

        return self.input_set

    def run(self, input_set):
        pass

    def plot(self):
        pass

class SystemCLI(CLI):
    model_class = None

    @property
    def source(self):
        return self.model_class

    def inputs(self):
        return self.model_class.inputs()

    def serialize_inputs(self):
        return dict(self.input_set.values)

    def load_inputs(self, values):
        self.input_set = InputSet(self.inputs())
        for input_name, input_value in values.items():
            self.input_set.set_value(input_name, input_value)

    def run(self):
        self.model = self.model_class()
        self.model.prepare(self.input_set)
        self.results = self.model.run()

class CementCLI(SystemCLI):
    model_class = cement.Cement

    def plot(self):
        return self.model.plot(self.results)

class IronSteelCLI(SystemCLI):
    model_class = iron_steel.IronSteel

    def prompt_inputs(self):
        super().prompt_inputs()
        if self.input_set.value('route') is None:
            route_input = self.input_set.input('route')
            self.input_set.set_value('route', prompt_input(route_input, self.input_set))

    def plot(self):
        return self.model.plot(self.results)

class AluminumCLI(SystemCLI):
    model_class = aluminum.Aluminum

    def plot(self):
        return self.model.plot(self.results)

class IndFleetCLI(SystemCLI):
    model_class = industrial_fleet.IndFleetModel

    def plot(self):
        return self.model.plot(self.results)

class FleetCLI(SystemCLI):
    model_class = fleet.FleetModel

    def plot(self):
        self.results['sales'].plot()
        plt.title('Sales')
        plt.show()

        self.results['stock'].plot()
        plt.title('Stock')
        plt.show()

        self.results['fuel'].plot()
        plt.title('Energy (kWh)')
        plt.show()

class GridCLI(SystemCLI):
    model_class = grid.Grid

    def plot(self):
        print(self.results)

class PPSCLI(SystemCLI):
    model_class = pps.PPS

    def plot(self):
        return self.model.plot(self.results)

class TEACLI(CLI):

    def prompt_inputs(self):
        self.source = prompt_options(tea_registry.analyses, 'TEA Analysis')
        return super().prompt_inputs()

    def serialize_inputs(self):
        return {
            'analysis': self.source.name,
            'inputs': dict(self.input_set.values),
        }

    def load_inputs(self, serialized):
        self.source = tea_registry.lookup_by_name(serialized['analysis'])
        self.input_set = InputSet(self.source.inputs())
        self.input_set.set_values(serialized['inputs'])

    def run(self):
        self.pathway = TeaPathway(self.source, self.input_set)
        self.results = tea_analysis.run(self.pathway)

    def plot(self):
        graph.plot(self.results, x='cost_category', group_by='cost_category_by_parts')

class LCACLI(CLI):

    def prompt_inputs(self):
        self._prompt_context()
        steps = []
        for source in self._prompt_pathway():
            if self.args.defaults:
                input_set = InputSet.build_default(source, context=self.context)
            else:
                input_set = prompt_inputs(source=source, context=self.context)

            input_set.context = dict(self.context)
            steps.append(Step(source, input_set))

        self.pathway = Pathway(steps)

    def serialize_inputs(self):
        return {
            'context': dict(self.context),
            'pathway': self.pathway.serialize(),
        }

    def load_inputs(self, serialized):
        self.context = dict(serialized['context'])
        self.pathway = Pathway.load(serialized['pathway'], context=self.context)

    def run(self):
        self.results = lca_analysis.run([self.pathway])
        if self.context['compute_cost']:
            self.tea_analysis = tea_registry.lookup_by_pathway_id(tea.pathway_id(self.pathway))
            self.tea_pathway = TeaPathway(self.tea_analysis, lca_pathway=self.pathway)
            self.tea_results = tea_analysis.run(self.tea_pathway)

        if self.args.group_by != 'sub_stage':
            self.results['data'] = self.results['data'].groupby(['pathway', 'stage']).agg({'value': 'sum'}).reset_index()

    def plot(self):
        graph.plot(self.results, x='stage', group_by=self.args.group_by)

        if self.context['compute_cost']:
            graph.plot(self.tea_results, x='cost_category', group_by='cost_category_by_parts')

    def _prompt_context(self):
        compute_cost = prompt_options([True, False], 'Compute Cost?')
        self.context = {
            'compute_cost': compute_cost,
        }

    def _prompt_pathway(self):
        stages = pathway_metadata.stages
        category = prompt_options(stages[0].get_categories(), stages[0].name + " Category")
        activities = stages[0].get_activities_by_category(category)

        while len(activities) > 0:
            label = f'{activities[0].stage} stage activity'
            activity = prompt_options(activities, label)
            source = prompt_options(activity.sources, 'Data source')
            yield source
            activities = activity.links


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--analysis', default='lca', help='name of analysis to perform', required=True)
    parser.add_argument('--defaults', help='use default inputs', dest='defaults', action='store_true'),
    parser.add_argument('--input', help='path to JSON file containing inputs')
    parser.add_argument('--output', help='path to JSON file in which to store collected inputs')
    parser.add_argument('--group-by', default='pathway', help='name of series with which to group results (default=pathway)')

    args = parser.parse_args()

    analyses = {
        'lca': LCACLI,
        'tea': TEACLI,
        'fleet': FleetCLI,
        'grid': GridCLI,
        'pps': PPSCLI,
        'cement': CementCLI,
        'steel': IronSteelCLI,
        'aluminum': AluminumCLI,
        'industrial_fleet': IndFleetCLI
    }

    if args.analysis not in analyses:
        analysis_names = ', '.join(analyses.keys())
        print(f'analysis must be one of: {analysis_names}')
        parser.print_usage()
        exit(1)

    cli = analyses[args.analysis](args)

    if args.input:
        with open(args.input, 'r') as f:
            data = json.load(f)
            cli.load_inputs(data)
    else:
        cli.prompt_inputs()

        if args.output:
            with open(args.output, 'w+') as f:
                data = cli.serialize_inputs()
                json.dump(data, f, indent=2)

    cli.run()
    cli.plot()

if __name__ == '__main__':
    main()
