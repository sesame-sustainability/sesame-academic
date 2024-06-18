class SystemAnalysis:

    def __init__(self, name, query, inputs, axes):
        self.name = name
        self.query = query
        self.inputs = inputs
        self.axes = axes

    def __str__(self):
        return self.name

    def run(self, input_set):
        params = input_set.values
        return self.query(**params)

    def serialize(self):
        return {
            'name': self.name,
            'user_inputs': [
                input.serialize()
                for input in self.inputs
            ],
            'axes': self.axes,
        }
