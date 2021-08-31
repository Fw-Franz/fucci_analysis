import os
import pandas as pd
import numpy as np
import seaborn as sns
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib
import matplotlib.pyplot as plt
import time
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from pylab import figure, text, scatter, show

start_time = time.time()

#region Input parameters
row_order=['E', 'C', 'D', 'B', 'F', 'G']   # order of rows by which to plot, Control must be first!, e.g. ['E', 'C', 'D', 'B', 'F', 'G']
plottype='bar' # 'box' or 'bar'
statistical_test = 'do_tukey_test' # currently only 'do_tukey_test'
plot_stats_stars=  True  # True or False  (no '')

normalization='_background_sub' # '' or '_background_sub'
analyze_method='Fold_change_' # '' or 'Fold_change_'  for graphing only
plot_column='FarRed_int_I'
control_condition='Control'
#endregion


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Custom_dir="D:\\Data_Lab\\Juanita\\Antibody_data\\cmycbestsettings\\"

root = tk.Tk()
root.withdraw()
filepath = filedialog.askopenfilename(
    initialdir="BASE_DIR",
    # initialdir="Custom_dir",
    title="Select file",
    filetypes=(("csv", "*.csv"),)
)

base_directory = os.path.dirname(os.path.abspath(filepath))

input_folder_name=os.path.basename(base_directory)

plot_context = 'talk'
# plot_context = 'notebook'
font_scale=1.5
save_plots=1


# endregion


column_name= analyze_method + plot_column + normalization

column_name_stats = plot_column + normalization

if plottype=='box':
    box_dir = os.path.join(
        base_directory, 'boxplots\\')
elif plottype=='bar':
    box_dir = os.path.join(
        base_directory, 'barplots\\')

if not os.path.exists(box_dir):
    os.makedirs(box_dir)

# ax_title_boxplot = f'Day {box_day} Normalized Cell Counts Compared to {control_condition} - frame m{frame}'

boxplot_fname = box_dir + column_name

print('Producing Combined Boxplot')

mi_box = pd.read_csv(filepath)

sorterIndex = dict(zip(row_order, range(len(row_order))))
mi_box['Drug_Rank'] = mi_box['Row'].map(sorterIndex)
mi_box.sort_values(['Drug_Rank'],
        ascending = [ True], inplace = True)
mi_box.drop('Drug_Rank', 1, inplace = True)

if statistical_test == 'do_tukey_test':
    print('Producing Tukey Analysis results')

    stats_dir = os.path.join(
        base_directory, 'stats\\')

    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)


    mi_tukey=mi_box.copy()

    Drug_list=mi_tukey['Drug_Name'].str.split(';\s*', expand=True).stack().unique()

    mi_tukey['sample_size_count']=mi_tukey['Drug_Name'].copy()
    mi_tukey['sample_size_count'] = mi_tukey.groupby(by='Drug_Name')['sample_size_count'].transform('count')

    m_day = mi_tukey.copy()

    result_05 = pairwise_tukeyhsd(
        m_day[column_name_stats], m_day['Drug_Name'], alpha=0.05
    )
    df_tukey = pd.DataFrame(
        data=result_05._results_table.data[1:],
        columns=result_05._results_table.data[0]
    )
    df_tukey['reject_05'] = (df_tukey['p-adj'] < 0.05)
    df_tukey['reject_01'] = (df_tukey['p-adj'] < 0.01)
    df_tukey['reject_001'] = (df_tukey['p-adj'] < 0.001)

    df_tukey['Sample_size_1'] = ''
    df_tukey['Sample_size_2'] = ''

    for con in Drug_list:
        df_tukey.loc[df_tukey.group1 == con, 'Sample_size_1'] = np.max(
            mi_tukey.loc[(mi_tukey.Drug_Name == con),
                         'sample_size_count'])
        df_tukey.loc[df_tukey.group2 == con, 'Sample_size_2'] = np.max(
            mi_tukey.loc[(mi_tukey.Drug_Name == con),
                         'sample_size_count'])

    df_tukey.to_csv(
        path_or_buf=stats_dir+ column_name_stats + '_Tukey.csv',
        index=None,
        header=True
    )

# if analyze_method=='Fold_change_':
#     mi_box=mi_box[mi_box.Drug_Name != control_condition]

swarmplot_size = 10
swarmplot_offset = 0  # offset to left of boxplot

# ax = sns.swarmplot(x="Condition", y=norm_colname, data=mi_box, hue="Date", size=swarmplot_size,
#                    edgecolor="white", linewidth=1, dodge=True)
# g = mi_box.groupby(by=["Condition"])[norm_colname].median()
medians=mi_box.median(axis=0)

# my_order = medians.nlargest(len(medians))
# my_order = my_order.index.tolist()

sns.set(context=plot_context,font_scale=font_scale,style="whitegrid")

# ax = sns.swarmplot(data=mi_box, size=swarmplot_size, order=my_order,
#                    edgecolor="black", linewidth=0.5)
# ax = sns.stripplot(data=mi_box, size=swarmplot_size, order=my_order,
#                    edgecolor="black", linewidth=1)
ax = sns.stripplot(x=mi_box["Drug_Name"], y=column_name, data=mi_box, size=swarmplot_size,
                   edgecolor="black", linewidth=1)


path_collections = [child for child in ax.get_children()
                    if isinstance(child, matplotlib.collections.PathCollection)]

for path_collection in path_collections:
    x, y = np.array(path_collection.get_offsets()).T
    xnew = x + swarmplot_offset
    offsets = list(zip(xnew, y))
    path_collection.set_offsets(offsets)

if plottype=='box':

    # ax = sns.boxplot(data=mi_box, order=my_order, linewidth=2, fliersize=0, showmeans=True,
    ax = sns.boxplot(x=mi_box["Drug_Name"], y=column_name, data=mi_box, linewidth=2, fliersize=0, showmeans=True,
                meanprops={"marker": "D",
                           "markeredgecolor": "white",
                           "markerfacecolor": "black",
                           "markersize": "14"})

elif plottype== 'bar':
    ax = sns.barplot(x=mi_box["Drug_Name"], y=column_name, data=mi_box,)

ax.grid(True)

bottom, top = ax.get_ylim()

fig = plt.gcf()
fig.set_size_inches(30, 15)
plt.gcf().subplots_adjust(bottom=0.3)

con_list = [item.get_text() for item in ax.get_xticklabels()]

conditions_labels = [w.replace('_', ' ') for w in con_list]

conditions_labels = [w.replace('uM', 'μM\n') for w in conditions_labels]

conditions_labels = [w.replace('mM', 'mM\n') for w in conditions_labels]
conditions_labels = [w.replace('nM', 'nM\n') for w in conditions_labels]
conditions_labels = [w.replace('per', '%') for w in conditions_labels]



dx = 50 / 72.
dy = 0.
rotation=37
tick_orientation='right'
ax.set_xticklabels(conditions_labels, rotation=rotation,
                   ha=tick_orientation)  # , rotation_mode="anchor")

ylabel_string=column_name.replace('_', ' ')

ax.set_ylabel(ylabel_string)

offset = matplotlib.transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)

# apply offset transform to all x ticklabels.
for label in ax.xaxis.get_majorticklabels():
    label.set_transform(label.get_transform() + offset)

ax.set_xlabel('')

ax.set_title('')
if plot_stats_stars:

    if statistical_test == 'do_tukey_test':

        sorterIndex_Drugs = dict(zip(Drug_list, range(len(Drug_list))))
        if sorterIndex_Drugs[control_condition] != 0:
            raise ValueError("control_condition is not the first condition, violating assumptions necessary for plotting")

        for condition, iii in sorterIndex_Drugs.items():
            # print(condition,iii)
            if condition == control_condition:
                continue
            query_str = f'((group1 == "{condition}" & group2 == "{control_condition}") | \
                  (group1 == "{control_condition}" & group2 == "{condition}"))'
            df_tukey_con = df_tukey.query(query_str)
            df_tukey_con = df_tukey_con.reset_index(drop=True)
            row = df_tukey_con.iloc[0]
            reject_05 = row['reject_05']
            reject_01 = row['reject_01']
            reject_001 = row['reject_001']

            ymin, ymax = ax.get_ylim()
            lines = ax.get_lines()
            categories = ax.get_xticks()

            if plottype == 'box':
                y = round(lines[3 + (iii-2) * 6].get_ydata()[0], 1)/round(lines[3].get_ydata()[0], 1)
                y_offset=0.6
            elif plottype == 'bar':
                y = round(ax.patches[iii].get_height(), 1)
                y_offset=0.3

            if reject_001:
                text(iii - 0.15, y + y_offset, '***', fontsize=40, color='black')
            elif reject_01:
                text(iii - 0.1, y + y_offset, '**', fontsize=40, color='black')
            elif reject_05:
                text(iii - 0.05, y + y_offset, '*', fontsize=40, color='black')



if save_plots:
    plt.savefig(boxplot_fname)
    plt.clf()
    plt.close()
else:
    plt.show()