import pandas as pd


def perform_tea(tea_result):
    data = []
    cost_breakdown = tea_result['cost_breakdown']
    for cost_category in cost_breakdown:
        if isinstance(cost_breakdown[cost_category], dict):
            for item in cost_breakdown[cost_category]:
                data.append({
                    'pathway': tea_result['pathway_name'],
                    'cost_category': cost_category,
                    'cost_category_by_parts': item,
                    'value': cost_breakdown[cost_category][item],
                })
        else:
            data.append({
                'pathway': tea_result['pathway_name'],
                'cost_category': cost_category,
                'cost_category_by_parts': cost_category,
                'value': cost_breakdown[cost_category],
            })

    df = pd.DataFrame(data, columns=['pathway', 'cost_category', 'cost_category_by_parts', 'value'])
    return df


def run(tea_pathway):
    data = pd.DataFrame()
    table = None
    results = tea_pathway.perform()
    cost_df = perform_tea(results)
    cost_df['pathway'] = tea_pathway.name
    data = data.append(cost_df[['value', 'cost_category', 'cost_category_by_parts', 'pathway']])
    table = results['table']

    return dict(
        title=f'TEA Cost Breakdown',
        unit=tea_pathway.unit,
        value='Cost',
        columns=['value', 'cost_category', 'cost_category_by_parts', 'pathway'],
        data=data,
        table=table,
    )
