import re

from core import conditionals
from core.inputs import InputSet

def prefix(name):
    return re.sub(r'[^A-Za-z0-9]+', '_', name).lower()

class ModelComposer:

    def __init__(self, models, selection_input_name):
        self.models = models
        self.selection_input_name = selection_input_name

    def merged_inputs(self):
        inputs = []

        for name, model in self.models:
            for input in model.inputs():
                inputs.append(self._transform_input(name, input))

        return inputs

    def prepare(self, full_input_set, model):
        # unprefix model's input set before preparing model
        inputs = model.__class__.inputs()
        model_input_set = InputSet(inputs, context=full_input_set.context)

        selection_input_value = full_input_set.value(self.selection_input_name)

        for input_name in model_input_set.inputs:
            prefixed_input_name = f'{prefix(selection_input_value)}_{input_name}'
            value = full_input_set.value(prefixed_input_name)
            model_input_set.set_value(input_name, value)

        model.prepare(model_input_set)

    def _transform_input(self, name, input):
        def prefix_conditionals(conditionals):
            for conditional in conditionals:
                dependent_name, val = conditional.args
                conditional.args = (f'{prefix(name)}_{dependent_name}', val)

        # each input must have a unique name
        input.name = f'{prefix(name)}_{input.name}'

        prefix_conditionals(input.conditionals)

        input.conditionals.append(conditionals.input_equal_to(self.selection_input_name, name))

        if input.input_type == 'options':
            for option in input.options:
                prefix_conditionals(option.conditionals)
        elif input.input_type == 'share_table':
            for row in input.rows:
                for cell in row.cells:
                    for default in cell.defaults:
                        prefix_conditionals(default.conditionals)

        if input.input_type != 'group':
            for default in input.defaults:
                prefix_conditionals(default.conditionals)
            for action in input.on_change_actions:
                if action['type'] == 'set_input_to':
                    target = action['target']
                    action['target'] = f'{prefix(name)}_{target}'

        for child_input in input.children:
            self._transform_input(name, child_input)

        return input