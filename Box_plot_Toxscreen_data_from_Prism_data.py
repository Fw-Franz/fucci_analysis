import os
import pandas as pd
import numpy as np
import seaborn as sns
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib
import matplotlib.pyplot as plt

# region input parameters
# 0: 1st, 1: , 2: , 3: , 4:
conditions_list_i=0




plot_context = 'talk'
# plot_context = 'notebook'
font_scale=1.5
save_plots=1

control_condition='Control_DMSO'
frame=1

# endregion


# 1st Condition list
conditions_1=['Control_DMSO', 'Pantoprazole_50uM', 'NS1643_20uM', 'Pantoprazole_100uM_NS1643_20uM']


conditions_list=[conditions_1]

conditions=conditions_list[conditions_list_i]

conditions_reduced=conditions[1:]

filepath = filedialog.askopenfilename(
    initialdir="/",
    # initialdir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\Fucci_analysis\\NG108_FUCCI_Used\\data\\",
    title="Select file",
    filetypes=(("csv", "*.csv"),)
)

base_directory = os.path.dirname(os.path.dirname(filepath))


normalize_search = filepath.find("_normalized_")
if normalize_search>0:
    analyze_method='fold_change' # 'fold_change' or ''
else:
    analyze_method=''

Percent_search = filepath.find("_Percent_")
if Percent_search>0:
    normalization='_Percent_' # 'Percent_' or ''
else:
    normalization=''

schroedinger_search = filepath.find("_Alive_")

if Percent_search>0:
    schroedinger='_Alive'
else:
    schroedinger='_Dead'

fname= 'Cell_Count' + schroedinger + normalization  + analyze_method
ylabel_string=fname.replace('_',' ')

box_dir = os.path.join(
    base_directory, 'boxplots',
    f'm{frame}'
)



if not os.path.exists(box_dir):
    os.makedirs(box_dir)

# ax_title_boxplot = f'Day {box_day} Normalized Cell Counts Compared to {control_condition} - frame m{frame}'

Groupt_title = ['1st List']


boxplot_fname = os.path.join(box_dir, f'{Groupt_title[conditions_list_i]} {fname} .png')

print('Producing Combined Boxplot')

mi_box = pd.read_csv(filepath)

# mi_box = mi_box.loc[mi_box['Condition'].isin(conditions)]
# sorterIndex = dict(zip(conditions, range(len(conditions))))


# mi_box = mi_box.reset_index(drop=True)

if analyze_method == 'fold_change':
    mi_box=mi_box[conditions_reduced]
else:
    mi_box=mi_box[conditions]



swarmplot_size = 10
swarmplot_offset = 0  # offset to left of boxplot

# ax = sns.swarmplot(x="Condition", y=norm_colname, data=mi_box, hue="Date", size=swarmplot_size,
#                    edgecolor="white", linewidth=1, dodge=True)
# g = mi_box.groupby(by=["Condition"])[norm_colname].median()
medians=mi_box.median(axis=0)

my_order = medians.nlargest(len(medians))
my_order = my_order.index.tolist()

sns.set(context=plot_context,font_scale=font_scale,style="whitegrid")

# ax = sns.swarmplot(data=mi_box, size=swarmplot_size, order=my_order,
#                    edgecolor="black", linewidth=0.5)
ax = sns.stripplot(data=mi_box, size=swarmplot_size, order=my_order,
                   edgecolor="black", linewidth=1)


path_collections = [child for child in ax.get_children()
                    if isinstance(child, matplotlib.collections.PathCollection)]

for path_collection in path_collections:
    x, y = np.array(path_collection.get_offsets()).T
    xnew = x + swarmplot_offset
    offsets = list(zip(xnew, y))
    path_collection.set_offsets(offsets)

ax = sns.boxplot(data=mi_box, order=my_order, linewidth=2, fliersize=0, showmeans=True,
            meanprops={"marker": "D",
                       "markeredgecolor": "white",
                       "markerfacecolor": "black",
                       "markersize": "14"})

ax.grid(True)

bottom, top = ax.get_ylim()

# if analyze_method == "fold_change":
#     ax.set(ylim=(bottom-0.2*np.abs(bottom), 0.1))
# else:
#     ax.set(ylim=(bottom-0.2*np.abs(bottom), top+0.2*np.abs(top)))


# if analyze_method == "fold_change":
#     ax.set(ylim=(bottom-0.25, 0.25))
# else:
#     ax.set(ylim=(bottom, top+0.2*np.abs(top)))

fig = plt.gcf()
fig.set_size_inches(30, 15)
plt.gcf().subplots_adjust(bottom=0.3)

# ax.set_xticklabels(conditions, rotation=90)
# ax.set(xticks=ttest_pvalues.columns, rotation=90)
if analyze_method == "fold_change":
    tick_list = np.r_[0:len(conditions_reduced)]
else:
    tick_list = np.r_[0:len(conditions)]
ax.set_xticks(tick_list)

con_list = [item.get_text() for item in ax.get_xticklabels()]

conditions_labels = [w.replace('_', ' ') for w in con_list]

conditions_labels = [w.replace('uM', 'μM\n') for w in conditions_labels]

conditions_labels = [w.replace('mM', 'mM\n') for w in conditions_labels]
conditions_labels = [w.replace('nM', 'nM\n') for w in conditions_labels]
conditions_labels = [w.replace('per', '%') for w in conditions_labels]

if len(conditions)<6:
    dx = 0.
    dy = 0.
    rotation=0
    tick_orientation='center'

elif len(conditions)>15:
    rotation=37
    dx = 24 / 72.
    dy = 0.
    conditions_labels = [w.replace('\n', ' ') for w in conditions_labels]
    # tick_orientation='center'
    tick_orientation='right'

else:
    rotation=37
    dx = 50 / 72.
    dy = 0.
    # tick_orientation='center'
    tick_orientation='right'



# Con_list = mi_box['Condition'].to_numpy()
# con_list = np.unique(Con_list)
# con_list = con_list.tolist()




# conditions_label_reduced = [w.replace('_', ' \n ') for w in conditions_reduced]
# conditions_label_reduced = [w.replace('uM', 'μM') for w in conditions_label_reduced]

ax.set_xticklabels(conditions_labels, rotation=rotation,
                   ha=tick_orientation)  # , rotation_mode="anchor")
# if analyze_method == "fold_change":
#     # ax.set_xticklabels(conditions_label_reduced, rotation=rotation, ha=tick_orientation)  # , rotation_mode="anchor")
#     if normalization == '_Percent_':
#         ax.set_ylabel('Percent (Fold Change to Control)')
#     else:
#         ax.set_ylabel('Cell Count (Fold Change to Control)')
#     # plt.axhline(y=0)
# else:
#     ax.set_xticklabels(conditions_labels, rotation=rotation, ha=tick_orientation)  # , rotation_mode="anchor")
# # for tick in ax.xaxis.get_majorticklabels():
# #     tick.set_horizontalalignment("right")
#     if normalization == '_Percent_':
#         ax.set_ylabel('Percent')
#     else:
#         ax.set_ylabel('Cell Count')


ax.set_ylabel(ylabel_string)


offset = matplotlib.transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)

# apply offset transform to all x ticklabels.
for label in ax.xaxis.get_majorticklabels():
    label.set_transform(label.get_transform() + offset)

# ax.set_xlabel('Conditions')
ax.set_xlabel('')

# ax.set_title(ax_title_boxplot)
ax.set_title('')

# ax.xaxis.set_ticks_position('none')
# ax.yaxis.set_ticks_position('none')
# ax.tick_params(direction='in')


if save_plots:
    plt.savefig(boxplot_fname)
    plt.clf()
    plt.close()
else:
    plt.show()