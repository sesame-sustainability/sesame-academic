from core.inputs import CategoricalInput, ContinuousInput, OptionsInput
from core.system import SystemAnalysis
from analysis.system.power_historic.queries import queries

analyses = {}

states = [row['state'] for row in queries.states()]
if len(states) == 0:
    # data must not be populated in the database
    # add a placeholder
    states.append('<placeholder>')

# FIXME: need to filter based on state
def years():
    year_range = queries.year_range()
    res = []
    if year_range['min_year'] is not None:
        res = [str(year) for year in range(int(year_range['min_year']),int(year_range['max_year']) + 1)]
    return res

analyses['hourly_generation'] = SystemAnalysis(
    'hourly_generation',
    queries.hourly_generation,
    [
        OptionsInput('state', 'State', options=states),
        CategoricalInput('start_year', 'Start year'),
        CategoricalInput('end_year', 'End year'),
    ],
    {
        'x': 'hour',
        'y': [
            {
                'name': 'generation',
                'type': 'column',
                'label': 'Generation',
                'unit': 'MW',
            },
            {
                'name': 'co2',
                'type': 'line',
                'label': 'CO₂',
                'unit': 'tons',
            }
        ],
    }
)

analyses['yearly_generation'] = SystemAnalysis(
    'yearly_generation',
    queries.yearly_generation,
    [
        OptionsInput('state', 'State', options=states),
        CategoricalInput('start_year', 'Start year'),
        CategoricalInput('end_year', 'End year'),
    ],
    {
        'x': 'year',
        'y': [
            {
                'name': 'emission_intensity',
                'type': 'column',
                'label': 'Emissions Intensity',
                'unit': 'tons CO₂ / MW',
            }
        ],
    }
)
