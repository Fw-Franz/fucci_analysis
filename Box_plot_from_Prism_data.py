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
# Groupt_title='TMZ '
# Groupt_title='Pantoprazole '
# Groupt_title='Control '
Groupt_title='Control NG108 '
Groupt_title='Pantoprazole NG108 '

conditions_list_i=4

replicates='biological'
box_day=6
# normalization_type='Total_total_normalized_norm_log2'
normalization_type='Total_total_fold_change_norm_log2_Control_DMSO'
norm_colname=normalization_type
analyze_method='fold_change'
# analyze_method='total_normalization'

plot_context = 'talk'
# plot_context = 'notebook'
save_plots=1


control_condition='Control_DMSO'
frame='ean'

# endregion


# TMX condition list
conditions_TMZ=['Control_DMSO', 'TMZ_50uM', '1perFBS_cAMP_1mM_Rapamycin_200nM', 'Pantoprazole_100uM_NS1643_50uM',
            'Pantoprazole_100uM_Retigabine_10uM', 'NS1643_50uM_TMZ_50uM', 'Pantoprazole_100uM_NS1643_20uM',
            'Pantoprazole_50uM_NS1643_50uM', 'Pantoprazole_100uM_TMZ_50uM' ,'Pantoprazole_100uM_Lamotrigine_100uM',
            'Pantoprazole_100uM_Rapamycin_150nM' ,'Pantoprazole_100uM_Rapamycin_100nM', 'NS1643_20uM_TMZ_50uM',
            'Rapamycin_100nM_TMZ_50uM', 'Rapamycin_150nM_TMZ_50uM', 'Pantoprazole_100uM']

# Pantoprazole list
conditions_Pantaprazole=['Control_DMSO', 'Pantoprazole_100uM' ,'Pantoprazole_100uM_NS1643_50uM' ,'Pantoprazole_100uM_Retigabine_10uM',
            'Pantoprazole_100uM_NS1643_20uM' ,'Pantoprazole_50uM_NS1643_50uM' ,'Pantoprazole_100uM_TMZ_50uM',
            'Pantoprazole_100uM_Lamotrigine_100uM' ,'Pantoprazole_100uM_Rapamycin_150nM',
            'Pantoprazole_100uM_Rapamycin_100nM']

# Control_DMSO condition list
conditions_Control=['Control_DMSO', 'Pantoprazole_100uM_Retigabine_10uM', '1perFBS_cAMP_1mM_Rapamycin_200nM',
        'Pantoprazole_100uM_NS1643_50uM', 'Pantoprazole_100uM_NS1643_20uM', 'Pantoprazole_100uM_Rapamycin_150nM',
        'Pantoprazole_100uM_Rapamycin_100nM', 'Pantoprazole_100uM_Lamotrigine_100uM', 'Pantoprazole_100uM_TMZ_50uM',
        'NS1643_50uM_TMZ_50uM', 'Rapamycin_100nM_TMZ_50uM', 'Lamotrigine_100uM_TMZ_50uM', 'Rapamycin_150nM_TMZ_50uM',
        'Pantoprazole_50uM_NS1643_50uM', 'Minoxidil_30uM_TMZ_50uM', 'NS1643_50uM_Rapamycin_100nM', 'NS1643_20uM_TMZ_50uM',
        'NS1643_50uM_Rapamycin_150nM', 'Pantoprazole_100uM', 'Retigabine_10uM_TMZ_50uM', 'Pantoprazole_50uM_Rapamycin_150nM',
        'Pantoprazole_50uM_Rapamycin_100nM', 'Pantoprazole_50uM_TMZ_50uM', 'Pantoprazole_50uM_Lamotrigine_100uM',
        'Pantoprazole_50uM_NS1643_20uM', 'TMZ_50uM', 'Chlorozoxazone_100uM_TMZ_50uM', 'NS1643_50uM',
        'Pantoprazole_100uM_Chlorozoxazone_100uM', 'NS1643_50uM_Chlorozoxazone_100uM', 'Retigabine_10uM_Rapamycin_100nM',
        'Retigabine_10uM_Rapamycin_150nM', 'Rapamycin_150nM', 'Rapamycin_100nM']

# Control_DMSO condition list
conditions_Control_NG108=['Control_DMSO' ,'1perFBS_cAMP_1mM_Rapamycin_200nM' ,'Pantoprazole_100uM_Rapamycin_100nM',
'Pantoprazole_100uM_NS1643_20uM' ,'Pantoprazole_100uM_Lamotrigine_100uM' ,'Pantoprazole_100uM_Retigabine_10uM',
'cAMP_1mM_Rapamycin_200nM' ,'Pantoprazole_100uM_TMZ_50uM' ,'Pantoprazole_50uM_Rapamycin_100nM',
'Pantoprazole_100uM' ,'NS1643_50uM_Rapamycin_100nM' ,'Pantoprazole_50uM_Retigabine_10uM',
'Pantoprazole_50uM_Lamotrigine_100uM' ,'Pantoprazole_50uM_NS1643_20uM' ,'Rapamycin_100nM_TMZ_50uM',
'Rapamycin_100nM' ,'NS1643_1uM_Rapamycin_100nM' ,'Rapamycin_150nM' ,'Retigabine_10uM_Rapamycin_100nM',
'NS1643_1uM_Rapamycin_150nM', 'Pantoprazole_50uM', 'NS1643_50uM', 'Minoxidil_30uM_Rapamycin_100nM',
'Minoxidil_30uM_Rapamycin_150nM' ,'NS1643_1uM_Retigabine_10uM' ,'Retigabine_10uM' ,'NS1643_20uM']

conditions_Pantaprazole_NG108=['Control_DMSO' ,'Pantoprazole_100uM' ,'Pantoprazole_100uM_Rapamycin_100nM' , 'Pantoprazole_100uM_NS1643_20uM' , 'Pantoprazole_100uM_Lamotrigine_100uM' ]

conditions_list=[conditions_TMZ,conditions_Pantaprazole, conditions_Control,conditions_Control_NG108,conditions_Pantaprazole_NG108]

conditions=conditions_list[conditions_list_i]

conditions_reduced=conditions[1:]

filepath = filedialog.askopenfilename(
    initialdir="/",
    # initialdir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\Fucci_analysis\\NG108_FUCCI_Used\\data\\",
    title="Select file",
    filetypes=(("csv", "*.csv"),)
)

base_directory = os.path.dirname(os.path.dirname(filepath))


box_dir = os.path.join(
    base_directory, 'plots', 'boxplots',
    f'{control_condition}_normalized',
    normalization_type, f'm{frame}'
)



if not os.path.exists(box_dir):
    os.makedirs(box_dir)

# ax_title_boxplot = f'Day {box_day} Normalized Cell Counts Compared to {control_condition} - frame m{frame}'

ax_title_boxplot = f'Day {box_day}'
boxplot_fname = os.path.join(box_dir, f'{Groupt_title} {control_condition} normalized {ax_title_boxplot}.png')

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

sns.set(context=plot_context,font_scale=1.5,style="whitegrid")

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

ax = sns.boxplot(data=mi_box, order=my_order, linewidth=2, fliersize=0)

ax.grid(True)

bottom, top = ax.get_ylim()

# if analyze_method == "fold_change":
#     ax.set(ylim=(bottom-0.2*np.abs(bottom), 0.1))
# else:
#     ax.set(ylim=(bottom-0.2*np.abs(bottom), top+0.2*np.abs(top)))
#
if analyze_method == "fold_change":
    ax.set(ylim=(bottom-0.25, 0.25))
else:
    ax.set(ylim=(bottom, top+0.2*np.abs(top)))

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
if analyze_method == "fold_change":
    # ax.set_xticklabels(conditions_label_reduced, rotation=rotation, ha=tick_orientation)  # , rotation_mode="anchor")
    ax.set_ylabel('Log2 (Fold Change to Control)')
    plt.axhline(y=0)
else:
    ax.set_xticklabels(conditions_labels, rotation=rotation, ha=tick_orientation)  # , rotation_mode="anchor")
# for tick in ax.xaxis.get_majorticklabels():
#     tick.set_horizontalalignment("right")
    ax.set_ylabel('Log2 (Fold Change to Day 0)')


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