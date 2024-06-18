## Setup

```
psql -d sesame -c "\copy grid_unit_genmap FROM './grid_unit_genmap.csv' DELIMITER ',' CSV HEADER;"
psql -d sesame -c "\copy loading_fraction FROM './loading_fraction.csv' DELIMITER ',' CSV HEADER;"
```

## Ingest

Ingest the EGRID data before ARP since it has more info about the individual plants:

```
python cli.py egrid_import --path=/path/to/egrid/directory
```

Download the ARP data for a given year:

```
python cli.py arp_download --year=2020
```

Import ARP data for a given date range:

```
python cli.py arp_import --start-date=01/2020 --end-date=09/2020
```

Or peform the imports async via a Redis-based worker queue:

```
python cli.py arp_import --start-date=01/2020 --end-date=09/2020 --enqueue
```

```
rqworker
```

(monitor the worker's progress via `rq-dashboard`)

Refresh the `arp_generation` view in the database:

```
REFRESH MATERIALIZED VIEW CONCURRENTLY arp_egrid_capacity;
REFRESH MATERIALIZED VIEW CONCURRENTLY arp_generation;
```

## Connecting to remote database

These scripts have been run on the EC2 instance hosting the PostgreSQL database.  To connect to that database remotely you can use the `psql` client:

```
psql postgresql://sesame:<PASSWORD>@ec2-54-82-208-13.compute-1.amazonaws.com/sesame
```

(where `<PASSWORD>` should be replaced with the actual password for the `sesame` user)

Or using a tool like `pgadmin`:

* host: `ec2-54-82-208-13.compute-1.amazonaws.com`
* port: `5432`
* username: `sesame`
* password

## Notes

* Currently skipping ARP rows for which no plant exists (i.e. was not present in the EGRID data):
  - orispl = 880041, 880075, 1393, 880100, 880107, 880079, 880053
