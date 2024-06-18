import numpy as np
from schematics.exceptions import ValidationError

class Validator:

    def __init__(self, name, fn, *args, message=None, warning=False):
        self.name = name
        self.fn = fn
        self.args = args
        self.message = message
        self.warning = warning

    def validate(self, value):
        # only raise an error if this is not a warning
        # TODO: maybe print out a warning in the CLI?
        if not self.warning:
            return self.fn(value, *self.args)

    def serialize(self):
        return {
            'name': self.name,
            'args': self.args,
            'message': self.message,
            'warning': self.warning,
        }

def validator(fn):
    def inner(*args, **kwargs):
        return Validator(fn.__name__, fn, *args, **kwargs)
    return inner

@validator
def numeric(value):
    if not (type(value) == int or type(value) == float or type(value) == np.float64):
        raise ValidationError(f'must be numeric')

@validator
def integer(value):
    if not (type(value) == int or type(value) == float):
        raise ValidationError(f'must be integer')
    if not value == int(value):
        raise ValidationError(f'must be integer')

@validator
def lt(value, n):
    if not value < n:
        raise ValidationError(f'must be less than {n}')

@validator
def gt(value, n):
    if not value > n:
        raise ValidationError(f'must be greater than {n}')

@validator
def lte(value, n):
    if not value <= n:
        raise ValidationError(f'must be less than or equal to {n}')

@validator
def gte(value, n):
    if not value >= n:
        raise ValidationError(f'must be greater than or equal to {n}')
