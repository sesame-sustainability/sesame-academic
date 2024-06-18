import importlib

def create_flow_object(name, value, unit):
    return {
        'name': name,
        'value': value,
        'unit': unit
    }

def load_class(module_path, class_name):
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

def yes_no(boolean):
    if boolean:
        return 'Yes'
    else:
        return 'No'
