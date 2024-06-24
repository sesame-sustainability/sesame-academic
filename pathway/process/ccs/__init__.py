import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
import core.validators as validators
from analysis.sensitivity import SensitivityInput

def user_inputs(tea=True, user_ci_default=None):
    use_user_ci_conditionals = [
        conditionals.input_equal_to('use_CCS', 'Yes'),
    ]

    if tea:
        use_user_ci_conditionals.append(conditionals.context_equal_to('compute_cost', False))

    ci_inputs = []
    if user_ci_default is None:
        ci_inputs.append(OptionsInput(
            'use_user_ci', 'Source of Compression Power',
            options=['User', 'Powerplant'],
            defaults=[Default('Powerplant')],
            conditionals=use_user_ci_conditionals,
            tooltip=Tooltip(
                'Life cycle carbon intensity of the power used for compressing captured CO2 for transportation to sequester site. Default for natural gas and coal plants is to use the electricity generated onsite.'
        )

        ))

    user_ci_defaults = []
    user_ci_conditionals = [conditionals.input_equal_to('use_CCS', 'Yes')]

    if user_ci_default is not None:
        user_ci_defaults.append(Default(user_ci_default))
    else:
        user_ci_conditionals.append(conditionals.input_equal_to('use_user_ci', 'User'))

    ci_inputs.append(ContinuousInput(
        'user_ci', 'Emissions of Compression Power',
        unit='gCO\u2082e/kWh',
        defaults=user_ci_defaults,
        validators=[validators.numeric(), validators.gte(0)],
        conditionals=user_ci_conditionals,
        tooltip=Tooltip(
            'Life cycle carbon intensity of the power used for compressing captured CO2 for transportation to sequester site. Default for natural gas and coal plants is to use the electricity generated onsite.'
        )

    ))

    return [
        OptionsInput(
            'use_CCS', 'Use CCS (Carbon Capture & Sequester)',
            options=['Yes', 'No'],
            defaults=[Default('No')],
            tooltip=Tooltip(
                'As a carbon mitigation technology, a CCS unit captures CO2 from a manufacturing plant and transport the captured CO2 to a sequestration site for long-term storage.',
            )

        ),
        ContinuousInput(
            'cap_percent_plant', 'CO\u2082 Captured from Plant',
            unit='%',
            defaults=[Default(85)],
            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
            conditionals=[conditionals.input_equal_to('use_CCS', 'Yes')],
            tooltip=Tooltip(
                'Percent of CO2, from the plant, captured by the CCS unit. Default 85% is from the NPC report, along with other emission and cost data from Tables 2-x. Also, the IEA study (e.g., Tables 7) shows that capital cost does not scale very non-linearly with capture %, so we assume linear scaling here, i.e., increasing capture % by 10% will increase capital cost by 10%. The same linearity is adopted for CCS energy consumption, because the NPC report assumes a fixed specific energy per CO2 captured amount. Thus, note that the further away from the default 85% capture, the less accurate our TEA results would be.',
                source='NPC 2020',
                source_link='https://www.energy.gov/sites/default/files/2021-06/2019%20-%20Meeting%20the%20Dual%20Challenge%20Vol%20II%20Chapter%202.pdf; https://ieaghg.org/publications/technical-reports/reports-list/9-technical-reports/1041-2020-07-update-techno-economic-benchmarks-for-fossil-fuel-fired-power-plants-with-co2-capture',
            )

        ),
    ] + ci_inputs + [
        ContinuousInput(
            'cap_percent_regen', 'CO\u2082 Captured from Amine Regeneration',
            unit='%',
            defaults=[Default(85)],
            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
            conditionals=[conditionals.input_equal_to('use_CCS', 'Yes'),],
            tooltip=Tooltip(
                'Amine regeneration for continuous CO2 capture requires heating. For CCS with natural gas/coal power plant, the heating source is natural gas/coal, respectively; for H2 production plant, the heating source is natural gas. If CO2 from such combustion processes is desired, then specify the capture %.',
                source='NPC 2020',
                source_link='https://www.energy.gov/sites/default/files/2021-06/2019%20-%20Meeting%20the%20Dual%20Challenge%20Vol%20II%20Chapter%202.pdf',
            )

        ),
        ContinuousInput(
            'pipeline_miles', 'Pipeline Distance from Capture to Sequester',
            unit='mi',
            defaults=[Default(240)],
            validators=[validators.numeric(), validators.gte(0)],
            conditionals=[conditionals.input_equal_to('use_CCS', 'Yes')],
            tooltip=Tooltip(
                'The distance could vary significantly by projects. 240 mi roughly translates to ~ 20 $/T CO2 for transportation and sequestration, assuming storage costs 8 $/T CO2, and transportation costs 0.05 $/T CO2/mi.',
                source='NPC 2020',
                source_link='https://dualchallenge.npc.org/files/CCUS-Chap_2-060520.pdf',
            )
        ),
    ]

@classmethod
def sensitivity(cls):
    return [
        SensitivityInput(
            'use_CCS',
            minimizing='Yes',
            maximizing='No',
            ),
        ]