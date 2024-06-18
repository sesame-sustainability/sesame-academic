class Conditional:

    def __init__(self, name, fn, *args):
        self.name = name
        self.fn = fn
        self.args = args

    def __repr__(self):
        return f"Conditional('{self.name}', {self.args})"

    def check(self, input_set):
        return self.fn(input_set, *self.args)

    def serialize(self):
        return {
            'name': self.name,
            'args': self.args
        }

def conditional(fn):
    def inner(*args):
        return Conditional(fn.__name__, fn, *args)
    return inner

@conditional
def input_equal_to(input_set, input_name, input_value):
    input = input_set.input(input_name)
    if not input:
        return False
    value = input_set.value(input_name)
    return input.is_relevant(input_set) and value == input_value

@conditional
def input_not_equal_to(input_set, input_name, input_value):
    input = input_set.input(input_name)
    value = input_set.value(input_name)
    return input.is_relevant(input_set) and value != input_value

@conditional
def input_greater_than(input_set, input_name, input_value):
    input = input_set.input(input_name)
    value = input_set.value(input_name)
    return input.is_relevant(input_set) and value > input_value

@conditional
def input_included_in(input_set, input_name, input_values):
    input = input_set.input(input_name)
    value = input_set.value(input_name)
    return input.is_relevant(input_set) and value in input_values

@conditional
def context_equal_to(input_set, context_key, context_val):
    return input_set.context.get(context_key, None) == context_val
