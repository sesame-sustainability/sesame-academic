"""Compare Emissions w/o and w/ CP, w/ CCS"""
"""https://www.tutorialspoint.com/matplotlib/matplotlib_bar_plot.htm"""

import matplotlib.pyplot as plt
fig,ax = plt.subplots()
elec_from_cp = [0,1.54336,0.817345283]
elec_from_grid = [ 1.7968, ( 1.7968-elec_from_cp[1]), (1.7968-elec_from_cp[2] )]
labels = ['BF w/o CP', 'BF w/ CP', 'BF w/ CP (no COG)']
ax.bar(labels,elec_from_grid)
ax.bar(labels,elec_from_cp,bottom=elec_from_grid)
ax.set_ylabel('Electricity (GJ)')
ax.set_title('Electricity Generation by Source')
ax.legend(labels = ['Grid','Captive Power'])
plt.show()