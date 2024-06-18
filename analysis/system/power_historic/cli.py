import argparse
from arp import import_csv
import egrid
import itertools
import os
from tqdm import tqdm
import us

def arp_range(args):
    start_month, start_year = [int(_) for _ in args.start_date.split('/')]
    end_month, end_year = [int(_) for _ in args.end_date.split('/')]
    states = [state.abbr.lower() for state in us.states.STATES]
    states = [state for state in states if state != 'hi']

    if args.start_state:
        states = list(itertools.dropwhile(lambda state: state != args.start_state, states))
    if args.end_state:
        states = list(itertools.takewhile(lambda state: state != args.end_state, states))
        states.append(args.end_state)

    if start_year == end_year:
        for state in states:
            for month in range(start_month, end_month + 1):
                yield (start_year, month, state)
    else:
        for state in states:
            for month in range(start_month, 13):
                yield (start_year, month, state)

        for year in range(start_year + 1, end_year):
            for state in states:
                for month in range(1, 13):
                    yield (year, month, state)

        for state in states:
            for month in range(1, end_month + 1):
                yield (end_year, month, state)

def egrid_import(args):
    imports = [
        # (file_name, sheet_name, header_index)
        ('eGRID2018_Data_v2.xlsx', 'PLNT18', 1),
        ('egrid2016_data.xlsx', 'PLNT16', 1),
        ('eGRID2014_Data_v2.xlsx', 'PLNT14', 1),
        ('eGRID2012_Data.xlsx', 'PLNT12', 4)
    ]

    for file_name, sheet_name, header_idx in imports:
        egrid.import_spreadsheet(os.path.join(args.path, file_name), sheet_name, header_idx)

def arp_download(args):
    year = args.year
    os.system(f'mkdir data; cd data; wget -r ftp://newftp.epa.gov/DMDnLoad/emissions/hourly/monthly/{year}/')
    os.system(f"cd data; unzip 'newftp.epa.gov/DMDnLoad/emissions/hourly/monthly/{year}/*.zip'")
    os.system('rm -rf ./data/newftp.epa.gov')

def arp_import(args):
    if args.enqueue:
        import redis
        import rq
        queue = rq.Queue(connection=redis.Redis())

        for (year, month, state) in arp_range(args):
            queue.enqueue(import_csv, year, month, state)
    else:
        for (year, month, state) in arp_range(args):
            try:
                import_csv(year, month, state)
            except FileNotFoundError:
                print(f'{month}/{year} {state} CSV not found')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    egrid_import_parser = subparsers.add_parser('egrid_import')
    egrid_import_parser.add_argument('--path', help='path to directory containing eGRID spreadhseets', required=True)

    arp_download_parser = subparsers.add_parser('arp_download')
    arp_download_parser.add_argument('--year', required=True)

    arp_import_parser = subparsers.add_parser('arp_import')
    arp_import_parser.add_argument('--start-date', help='starting date (i.e. MM/YYYY)', required=True)
    arp_import_parser.add_argument('--end-date', help='ending date (i.e. MM/YYYY)', required=True)
    arp_import_parser.add_argument('--start-state', help='starting state (i.e. ca)', required=False)
    arp_import_parser.add_argument('--end-state', help='ending state (i.e. ny)', required=False)
    arp_import_parser.add_argument('--enqueue', help='enqueue the imports to be performed later', required=False, action='store_true')

    args = parser.parse_args()

    if args.command == 'egrid_import':
        egrid_import(args)
    elif args.command == 'arp_download':
        arp_download(args)
    elif args.command == 'arp_import':
        arp_import(args)
