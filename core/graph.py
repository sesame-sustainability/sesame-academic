import matplotlib.pyplot as plt

from analysis.lca import perform_lcia

def plot(analysis_result, x, y='value', group_by=None):
    df = analysis_result['data'].pivot_table(index=x, values=y, columns=group_by)
    df.plot(kind='bar', stacked=True, rot=0)

    plt.title(analysis_result['title'], fontweight='bold', fontsize=14)
    plt.xlabel(x, fontweight='bold', fontsize=14)

    unit = analysis_result['unit']
    value = analysis_result['value']
    plt.ylabel(unit, fontweight='bold', fontsize=14)
    plt.yticks(fontweight='bold', fontsize=14)
    plt.xticks(fontweight='bold', fontsize=14)
    plt.show()


def plot_lcia_multiple_pathways(multiple_pathways, indicator="GWP"):
    stack_df = perform_lcia(multiple_pathways, indicator)
    #Greys
    stack_df.plot.bar(stacked=True, width=0.40, figsize=(12, 7))
    plt.title("LCIA - {}  for Multiple Pathways".format(indicator), fontweight="bold", fontsize=14)
    plt.ylabel("Emissions in kg", fontweight="bold", fontsize=14)
    plt.xticks(fontweight='bold', fontsize=14, rotation=0)
    plt.savefig("multiple_pathways/stacked_plot.png")
    plt.show()

    return plt
