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
import glob

start_time = time.time()

#region Input parameters
load_raw_data=False

sets=['set1','set2']
# sets=['set2']
days=['Day3','Day6']
dye_conditions=['dyewithdrug','justdye','withdrugafterlast']

# only change this to plot various settings
Dye_condition='withdrugafterlast'

# currently ignored as data is being pooled where available
sets_list=['set1',
           'set1',
           'set1',
           'set1',
           'set2',
           'set1',
           'set1',
           'set2',
           'set2']

# currently ignored as data is being pooled where available
# sets_list=['set2',
#            'set2',
#            'set2',
#            'set2']

conditions_list=['Control',
                'Pantoprazole_100uM',
                'NS1643_50uM',
                'Retigabine_10uM',
                'TMZ_50uM',
                'Pantoprazole_100uM_NS1643_50uM',
                'Pantoprazole_100uM_Retigabine_10uM',
                'Pantoprazole_100uM_TMZ_50uM',
                'NS1643_50uM_TMZ_50uM']


# conditions_list=['Control',
#                 'TMZ_50uM',
#                 'Pantoprazole_100uM_TMZ_50uM',
#                 'NS1643_50uM_TMZ_50uM']

# order of rows by which to plot, Control must be first!, e.g. ['E', 'C', 'D', 'B', 'F', 'G']

# conditions_list_reordered=['Control',
#                            'Pantoprazole_100uM',
#                            'NS1643_50uM',
#                            'Retigabine_10uM',
#                            'TMZ_50uM',
#                            'Pantoprazole_100uM_NS1643_50uM',
#                            'Pantoprazole_100uM_Retigabine_10uM',
#                            'Pantoprazole_100uM_TMZ_50uM',
#                            'NS1643_50uM_TMZ_50uM']

conditions_list_reordered=conditions_list

save_dir='DiBAC'

label_type='legend' # 'xaxis' or 'legend'
swarmplots=False

plottype='bar' # 'box' or 'bar'
bar_width=0.08
y_max=2

statistical_test = 'do_tukey_test' # currently only 'do_tukey_test'
plot_stats_stars=  False  # True or False  (no '')

normalization='' # '' or '_background_sub'
analyze_method='Fold_change_' # '' or 'Fold_change_'  for graphing only
plot_column='GFP_mean_I'
control_condition='Control'
#endregion

# Custom_dir=os.getcwd()
Custom_dir="E:\\NewAnalysisSheetsAll8_29_21\\New_Dye sheets\\DiBac_Sheets"

base_directory = Custom_dir

plot_context = 'talk'
# plot_context = 'notebook'
font_scale=3
save_plots=1

if load_raw_data:
    # for day in days:
    #     for set in sets:
    #         if day =='Day1':
    #             for dye in dye_conditions:
    filelist = glob.glob(base_directory + '\\U87_DiBAC4_3_' + '**/*DiBACResults_Column_means.csv', recursive=True)

    mi = pd.read_csv(filelist[0])
    mi=mi[0:0]

    for file in filelist:
        mi_inter = pd.read_csv(file)
        subdir = os.path.dirname(os.path.abspath(file))
        input_folder_name = os.path.basename(subdir)

        for day in days:
            if file.__contains__(day):
                mi_inter['day'] = day

        for set in sets:
            if file.__contains__(set):
                mi_inter['set'] = set

        for dye in dye_conditions:
            if file.__contains__(dye):
                mi_inter['Antibody'] = dye

        print(mi_inter.shape)

        mi=mi.append(mi_inter)

    print('saving....',mi.shape)
    mi.to_csv(path_or_buf=base_directory + '//Combined_DiBAC_AntibodyResults_Column_means.csv',  index=None, header=True)
else:
    mi=  pd.read_csv(base_directory+'//Combined_DiBAC_AntibodyResults_Column_means.csv')

if analyze_method=='Fold_change_':
    mi=mi.loc[mi.Drug_Name!='Control']
# region pre plotting configurations

if Dye_condition=='withdrugafterlast':
    Day='Day6'
else:
    Day='Day3'
mi_box=mi.copy()
mi_box=mi_box[0:0]

for i in range(0,len(conditions_list)):
    mi_box=mi_box.append(mi.loc[(mi.Antibody==Dye_condition) & (mi.Drug_Name==conditions_list[i]) & (mi.set==sets_list[i]) & (mi.day==Day)])
    # mi_box=mi_box.append(mi.loc[(mi.Antibody==Dye_condition) & (mi.Drug_Name==conditions_list[i])  & (mi.day==Day)])

mi_box['emtpy_column']=''

input_folder_name=os.path.basename(base_directory)

column_name= analyze_method + plot_column + normalization

# column_name_stats = plot_column + normalization
column_name_stats = column_name

if plottype=='box':
    box_dir = os.path.join(
        base_directory,  save_dir + '_stats_and_graphs\\boxplots\\')
elif plottype=='bar':
    box_dir = os.path.join(
        base_directory,  save_dir + '_stats_and_graphs\\barplots\\')

if not os.path.exists(box_dir):
    os.makedirs(box_dir)

# ax_title_boxplot = f'Day {box_day} Normalized Cell Counts Compared to {control_condition} - frame m{frame}'

boxplot_fname = box_dir + column_name +"_"+Day+"_"+Dye_condition

if plottype=='box':
    print('Producing Combined Boxplot')
elif plottype=='bar':
    print('Producing Combined Barplot')

sorterIndex = dict(zip(conditions_list_reordered, range(len(conditions_list_reordered))))
mi_box['Drug_Rank'] = mi_box['Drug_Name'].map(sorterIndex)
mi_box.sort_values(['Drug_Rank'],
        ascending = [ True], inplace = True)
mi_box.drop('Drug_Rank', 1, inplace = True)

#endregion

if statistical_test == 'do_tukey_test':
    print('Producing Tukey Analysis results')

    stats_dir = os.path.join(
        base_directory, save_dir + '_stats_and_graphs\\stats\\')

    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)


    mi_tukey=mi_box.copy()

    Drug_list=mi_tukey['Drug_Name'].str.split(';\s*', expand=True).stack().unique()

    mi_tukey['sample_size_count']=mi_tukey['Drug_Name'].copy()
    mi_tukey['sample_size_count'] = mi_tukey.groupby(by='Drug_Name')['sample_size_count'].transform('count')

    m_day = mi_tukey.copy()
    if column_name_stats.__contains__('Percent'):
        if m_day[column_name_stats].min()==0.0:
            m_day[column_name_stats] = 1 / 100 * m_day[column_name_stats].map(np.sqrt)
            m_day[column_name_stats] = m_day[column_name_stats].map(np.arcsin)
        else:
            m_day[column_name_stats] = 1 / 100 * m_day[column_name_stats].map(sp.special.logit)
    elif column_name_stats.__contains__('Fold_change'):
        m_day[column_name_stats]=m_day[column_name_stats].map(np.log10)

    result_05 = pairwise_tukeyhsd(
        m_day[column_name_stats], m_day['Drug_Name'], alpha=0.001
    )
    df_tukey = pd.DataFrame(
        data=result_05._results_table.data[1:],
        columns=result_05._results_table.data[0]
    )
    df_tukey['reject_05'] = (df_tukey['p-adj'] < 0.05)
    df_tukey['reject_01'] = (df_tukey['p-adj'] < 0.01)
    df_tukey['reject_001'] = df_tukey['reject']

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
        path_or_buf=stats_dir+ column_name_stats+"_"+Day+"_"+Dye_condition + '_Tukey.csv',
        index=None,
        header=True
    )




medians=mi_box.median(axis=0)

sns.set(context=plot_context,font_scale=font_scale,style="whitegrid")

if swarmplots:
    swarmplot_size = 10
    swarmplot_offset = 0  # offset to left of boxplot
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
    if label_type == 'xaxis':
        ax = sns.barplot(x=mi_box.Drug_Name, y=column_name, data=mi_box,capsize=0.05)
    else:

        # ['#0173b2', '#de8f05', '#029e73', '#d55e00', '#cc78bc', '#ca9161', '#fbafe4', '#949494', '#ece133', '#56b4e9']
        mypalette = {"Control": "black","Pantoprazole_100uM": "#949494",
        # mypalette = {"Pantoprazole_100uM": "#949494",
                     "Retigabine_10uM": "#029e73",
                     "Pantoprazole_100uM_Retigabine_10uM": "mediumaquamarine",
                     "Pantoprazole_100uM_NS1643_50uM": "lightskyblue",
                     "Pantoprazole_100uM_TMZ_50uM": "chocolate",
                     "NS1643_50uM_TMZ_50uM": "mediumorchid",
                     # "TMZ_50uM":"firebrick",
                     "TMZ_50uM":"saddlebrown",
                     "NS1643_50uM":"#0173b2"}

        # ax = sns.barplot(x=mi_box.emtpy_column, y=column_name, data=mi_box,hue="Drug_Name", capsize=0.05,
        #                  palette=sns.color_palette("colorblind"))#
        ax = sns.barplot(x=mi_box.emtpy_column, y=column_name, data=mi_box, hue="Drug_Name", capsize=0.05,
                         palette=mypalette)  #
        # ax = sns.barplot(x=mi_box.emtpy_column, y=column_name, data=mi_box,hue="Drug_Name", capsize=0.05,
        #                  palette=sns.color_palette("Greys"),saturation=4)#
        def change_width(ax, new_value):
            for patch in ax.patches:
                current_width = patch.get_width()
                diff = current_width - new_value

                # we change the bar width
                patch.set_width(new_value)

                # we recenter the bar
                patch.set_x(patch.get_x() + diff * .5)


        change_width(ax, bar_width)

ax.grid(True)
ax.set_ylim(ymax=y_max)

bottom, top = ax.get_ylim()

fig = plt.gcf()
fig.set_size_inches(30, 15)

if label_type == 'xaxis':
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

else:

    plt.gcf().subplots_adjust(right=0.7)
    handles, labels = ax.get_legend_handles_labels()
    labels = [w.replace('_', ' ') for w in labels]

    labels = [w.replace('uM', 'μM') for w in labels]

    labels = [w.replace('mM', 'mM') for w in labels]
    labels = [w.replace('nM', 'nM') for w in labels]
    labels = [w.replace('per', '%') for w in labels]

    ax.legend(handles=handles[0:], labels=labels[0:],loc='center left', bbox_to_anchor=(1, 0.5))

    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)  # labels along the bottom edge are off
    # plt.legend()

ax.set_xlabel('')

plt.axhline(y=1, color='black',linewidth=3, linestyle='--')

ax.set_ylabel('Fluorescence Intensity (FC)')

ax.set_title('')
if plot_stats_stars:

    if statistical_test == 'do_tukey_test':

        sorterIndex_Drugs = dict(zip(Drug_list, range(len(Drug_list))))

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