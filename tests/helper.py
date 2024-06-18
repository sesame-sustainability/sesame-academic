from core.inputs import InputSet
from core.pathway import Pathway, Step
import random
from pathway.topology import metadata as pathway_metadata
import json

def _filter_activities(activities):
    return [
        activity
        for activity in activities
        if len(activity.sources) > 0
    ]

def random_pathway():
    steps = []
    activities = _filter_activities(pathway_metadata.stages[0].activities)

    while len(activities) > 0:
        activity = random.choice(activities)
        source = random.choice(activity.sources)

        obj = source.instantiate()
        input_set = InputSet(source.inputs())

        for i, input in enumerate(input_set.inputs.values()):
            if input.input_type == 'categorical':
                obj.prepare(input_set)
                options = obj.categorical_options(input)
                if len(options) > 0:
                    input_set.set_value(input.name, random.choice(options))
            elif hasattr(input, 'options'):
                option = input.options[0]
                input_set.set_value(input.name, option.value)
            else:
                input_set.set_value(input.name, random.randint(10, 90))

        steps.append(Step(source, input_set))
        activities = _filter_activities(activity.links)

    return Pathway(steps)

def random_input_set(source):
    input_set = InputSet.build_empty(source)
    for input in input_set.inputs.values():
        if input.is_relevant(input_set):
            if input.input_type == 'options':
                option = random.choice(input.relevant_options(input_set))
                input_set.set_value(input.name, option.value)
            elif input.input_type == 'share_table':
                total = 100
                values = []
                for i in range(len(input.rows)):
                    value = random.randint(0, total)
                    total -= value
                    values.append(value)
                input_set.set_value(input.name, json.dumps(values))
            elif input.input_type == 'continuous':
                min = 0
                max = 100
                if len(input.validators) > 0:
                    for validator in input.validators:
                        if validator.name == 'gt':
                            min = validator.args[0] + 1
                        elif validator.name == 'gte':
                            min = validator.args[0]
                        elif validator.name == 'lt':
                            max = validator.args[0] - 1
                        elif validator.name == 'lte':
                            max = validator.args[0]
                input_set.set_value(input.name, random.randint(min, max))

    return input_set
