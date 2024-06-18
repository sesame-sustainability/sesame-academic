# sesame-core

SESAME core Python libraries and HTTP service

| Develop | Production |
| --- | --- |
| ![CodeBuild](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiSlFZSURSa3NRbjRDWXliSTVYcGdFVXlZNHJhUWR0bXFMdUpHOVVPNDUxelZmV1VSV0M0RTRVc1F4QnFOYk5lRkdId1B1M0krN3hKL1JnVSt2cERnMlowPSIsIml2UGFyYW1ldGVyU3BlYyI6Im1HWkp6TjNZMm1kQlp1NFIiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=develop) | ![CodeBuild](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiS000a2pydkRXTFNCV0NBOWVYYWNqNkZTc1A1OURLME03OXp4NUtrL1QydTUweGZVYS9yQlkvSm9SWEM0endYNVprd1hhRE5EbDQxTmNrYXFKTzhMVnEwPSIsIml2UGFyYW1ldGVyU3BlYyI6IkFhaDRuc1V5Y3N5ZUhlSGUiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=prod) |


## System Requirements

* Python 3.8.5
* Postgres 12.6
* [TimescaleDB extension](https://docs.timescale.com/v0.9/main)

## Setup

```
pip install -r requirements.txt
cp .env.example .env # customize as needed
```

```
createdb sesame
psql -d sesame -f schema.sql
```

Creating a user:

```
python -m core.users create --email=user@example.com --password=supersecret
```

## Testing

To run the full test suite:

```
python -m pytest
```

## CLI usage

```
usage: cli.py [-h] --analysis ANALYSIS [--defaults] [--input INPUT] [--output OUTPUT] [--group-by GROUP_BY]

optional arguments:
  -h, --help           show this help message and exit
  --analysis ANALYSIS  name of analysis to perform
  --defaults           use default inputs
  --input INPUT        path to JSON file containing inputs
  --output OUTPUT      path to JSON file in which to store collected inputs
  --group-by GROUP_BY  name of series with which to group results (default=pathway)
```

Current available analyses are:

* `lca`
* `tea`
* `fleet`
* `grid`
* `pps`
* `cement`
* `steel`
* `aluminum`
* `industrial_fleet`

To save the created pathway, specify an `output` directory:

```
python cli.py --output=path/to/pathway.json ...
```

To perform an analysis on a saved pathway, specify the pathway file as an input:

```
python cli.py --input=path/to/pathway.json ...
```

To use the default input values:

```
python cli.py --defaults ...
```

## HTTP server


To run the HTTP server:

```
flask run
```

#### Endpoints

**`GET /<module>/metadata`**

**`GET /<module>/user_inputs/<input_name>`**

**`POST /<module>/analysis`**

Where `<module>` is one of:

* `pathway`
  - no `analysis` endpoint
  - user input endpont requires `source_id`:
    - `GET /pathway/sources/<source_id>/user_inputs/<input_name>`
* `lca`
* `tea`
  - user input endpoint requires `analysis_name`:
    - `GET /tea/analyses/<analysis_name>/user_inputs/<input_name>`
* `fleet`
* `power_historic`
  - user input endpoint requires `analysis_name`:
    - `GET /power_historic/<analysis_name>/user_inputs/<input_name>`
* `grid`
* `pps`
* `industry/cement`
* `industry/steel`
* `industry/aluminum`
* `industry/fleet`

## Development

**File structure:**

* `core/` - Contains library classes and functions that provide the main abstractions to support other parts of the codebase
* `pathway/` - Activity source definitions for all possible steps in a pathway.  Each class declares the set of user inputs on which it depends and performs emissions calculations for that step in the pathway.
* `pathway/topology.py` - Defines the full topology of stages, activities and sources as well as the linkages between activities.
* `analysis/` - Code for performing higher-level analysis (i.e. LCA, TEA)
* `app/` - Contains all Flask-related code that comprises the HTTP API
* `tests/` - Automated testing code
* `deploy/` - Ansible playbooks for deployment

**Defining a new activity source:**

1. Create a new file somewhere in the relevant `pathway/<stage_name>` directory
2. In that file, define a class that inherits from `core.pathway.ActivitySource`:

    ```python
    from core.pathway import ActivitySource

    class MyActivtySource(ActivitySource):
        pass
    ```

3. Register the activity source in `pathway/topology.py`:

    ```python
    from core.utils import load_class

    some_activity.register_source(
      'MyActivitySource',
      load_class('path.to.new.module', 'MyActivitySource')
    )
    ```

    If the activity source depends on a lookup table then specify that file as well:

    ```python
    some_activity.register_source(
      'MyActivitySource',
      load_class('path.to.new.module', 'MyActivitySource'),
      table='path/to/table.csv'
    )
    ```

4. Optionally specify any user inputs in the activty source class:

    ```python
    from core.inputs import CategoricalInput, ContinuousInput
    import core.validators as validators

    class MyActivitySource(ActivitySource):

        @classmethod
        def user_inputs(cls):
            return [
                CategoricalInput('example1', 'Some Categorical Input'),
                ContinuousInput('example2', 'Some Continuous Input', validators=[
                    validators.numeric(), validators.gte(0), validators.lt(100)
                ])
            ]
    ```

4.  Optionally specify any data table filters that should be applied (this impacts the rows over which computations will be applied):

    ```python
    class MyActivitySource(ActivitySource):

        filters = [
            ('Column Name', 'Value')
        ]
    ```

    This filters the applicable rows in the lookup table down to those with `Column Name` equal to `Value`.

5. Implement a `get_inputs` method:

    ```python
    class MyActivitySource(ActivitySource):

        def get_inputs(self):
            ...

            return {
                'primary': ...,
                'secondary': ...
            }
    ```

6. Implement a `get_emissions` method:

    ```python
    class MyActivitySource(ActivitySource):

        def get_emissions(self):
            return ...
    ```

    There are some useful methods available to the `ActivitySource` subclass that may be helpful in computing the inputs and emissions:

    * `self.data_frame()` - returns the data frame loaded from the lookup table with class `filters` applied
    * `self.filtered_data_frame()` - returns subset of rows with `filters` applied as well as any categorical user inputs
