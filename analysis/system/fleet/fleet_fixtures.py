
import json
from tqdm import tqdm
import random

from analysis.system.fleet.fleet import FleetModel
from core.common import JSONEncoder
import tests.helper as helper

class FleetJSONEncoder(JSONEncoder):

    def _value(self, value):
        if isinstance(value, float):
            return format(value, '.10f')
        else:
            return super()._value(value)

def fleet_run(input_values):
    fleet = FleetModel()
    fleet.set_user_inputs(input_values)
    fleet.set_defaults()

    return {
        'inputs': input_values,
        'results': fleet.compute_outputs(),
    }

def fleet_verify(fixture):
    data = json.loads(fixture)
    output = json.dumps(fleet_run(data['inputs']), cls=FleetJSONEncoder)
    return output == fixture

def fleet_fixture():
    input_set = helper.random_input_set(FleetModel)
    return json.dumps(fleet_run(input_set.values), cls=FleetJSONEncoder)

if __name__ == '__main__':
    import argparse
    import uuid
    import os

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    save_parser = subparsers.add_parser('save')
    save_parser.add_argument('-n', required=True, type=int)
    save_parser.add_argument('--output-dir', required=True)

    verify_parser = subparsers.add_parser('verify')
    verify_parser.add_argument('--dir')
    verify_parser.add_argument('-n', type=int)
    verify_parser.add_argument('--num-workers', type=int, default=4)
    verify_parser.add_argument('--path')

    args = parser.parse_args()

    if args.command == 'save':
        for i in tqdm(range(args.n)):
            name = str(uuid.uuid4())
            path = os.path.join(args.output_dir, f'{name}.json')
            with open(path, 'w') as f:
                f.write(fleet_fixture())

    elif args.command == 'verify':
        files = []
        if args.dir:
            files = [
                os.path.join(args.dir, name)
                for name in os.listdir(args.dir)
            ]
            if args.n:
                files = random.sample(files, args.n)
        elif args.path:
            files = [args.path]
            print(files)
        else:
            print('error: must specify --dir or --path')
            parser.print_help()
            exit(1)

        for path in tqdm(files):
            with open(path, 'r') as f:
                if not fleet_verify(f.read()):
                    raise Exception(f'fixture error: {name}')

    else:
        parser.print_help()
        exit(1)
