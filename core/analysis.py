analyses = {}


class Param:

    def __init__(self, name, label, options):
        self.name = name
        self.label = label
        self.options = options

    def serialize(self):
        return {
            'name': self.name,
            'label': self.label,
            'options': self.options
        }

    def is_valid_option(self, value):
        return value in [item['value'] for item in self.options]


class Analysis:

    def __init__(self, name, fn, label=''):
        self.name = name
        self.label = label
        self.fn = fn
        self.params = []

    def register_param(self, **kwargs):
        self.params.append(Param(**kwargs))

    def serialize(self):
        return {
            'name': self.name,
            'label': self.label,
            'params': [param.serialize() for param in self.params]
        }


class AnalysisResult:

    def __init__(self, title='', unit=None, value=None, columns=[], params={}, data=[]):
        self.title = title
        self.unit = unit
        self.value = value
        self.columns = columns
        self.params = params
        self.data = data

    def serialize(self):
        return {
            'title': self.title,
            'unit': self.unit,
            'value': self.value,
            'columns': self.columns,
            'params': self.params,
            'data': [
                item.tolist()
                for item in self.data.to_numpy()
            ]
        }


def result(**kwargs):
    return


def analysis(name, **kwargs):
    def register(fn):
        analysis = Analysis(name, fn, **kwargs)
        analyses[name] = analysis
        return analysis

    return register


def param(**kwargs):
    def inner(analysis):
        analysis.register_param(**kwargs)
        return analysis

    return inner


def run(name, pathways, **params):
    analysis = analyses[name]
    if analysis is None:
        raise Exception(f'no such analysis: {name}')

    res = analysis.fn(pathways, **params)
    return AnalysisResult(**res)
