import numpy as np
import seaborn as sns
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import statsmodels.stats.multicomp
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
from pylab import figure, text, scatter, show
from collections import OrderedDict
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import time
import os
import sys
import data_annotation
import pingouin as pg

pd.options.mode.chained_assignment = 'raise'

TOTAL_NORM = 'total'
RELATIVE_NORM = 'relative'
NORMALIZATION_TYPES = [
    TOTAL_NORM,
    RELATIVE_NORM
]
NORMALIZED_METHOD = 'normalized'
RAW_METHOD = 'raw'
FOLD_CHANGE_METHOD = 'fold_change'

NORMAL_SCALE='normal'
LOG2_SCALE='log2'
DATA_SCALE_METHODS = [
    NORMAL_SCALE,
    LOG2_SCALE
]
ANALYZE_METHODS = [
    NORMALIZED_METHOD,
    RAW_METHOD,
    FOLD_CHANGE_METHOD
]

TTEST='do_ttest'
WILCOXIN='do_wilcoxon_test'
ANOVA='do_anova'
TUKEY='do_tukey_test'
GAMESHOWELL='do_gameshowell_test'


STATS_METHODS = [
    TTEST,
    WILCOXIN,
    TUKEY,
    GAMESHOWELL
]

TECHNICAL = 'technical'
BIOLOGICAL = 'biological'

REPLICATES = [
    TECHNICAL,
    BIOLOGICAL
]

STATS_VARS_TYPES = ['Total', 'Cell_percent']
# X_VAR_TYPES = ['Day']
PLOT_CONTEXT_TYPES = ['talk', 'poster', 'notebook']
FONT_SCALE_TYPES = [0.5, 0.8, 1.0, 1.2, 1.5, 2]
# HUE_SPLIT_TYPES = ['Condition', 'Percent']


def create_plots_and_stats(stats_vars, filepaths, normalization_type, data_scale,
# def create_plots_and_stats(stats_vars, x_var, filepaths, normalization_type, data_scale,
        # analyze_method, plot_context, hue_split,
        analyze_method, statistical_test, replicates, plot_context, font_scale,
        control_condition=None, conditions_override=None,
        plots=False, save_plots=False, colormap_plot=False, cmap_discrete=False,
        individual_plots=False, boxplots=False, box_day=None, stackedbarplots=False, lineplots=False,
        do_stats=False, save_excel_stats=False):

    error_msgs = []
    if normalization_type not in NORMALIZATION_TYPES:
        error_msgs.append(f'Invalid normalization_type: {normalization_type}.')
    if analyze_method not in ANALYZE_METHODS:
        error_msgs.append(f'Invalid analyze_method: {analyze_method}.')
    # if x_var not in X_VAR_TYPES:
    #     error_msgs.append(f'Invalid x_var: {x_var}.')
    if plot_context not in PLOT_CONTEXT_TYPES:
        error_msgs.append(f'Invalid plot_context: {plot_context}.')
    # if hue_split not in HUE_SPLIT_TYPES:
    #     error_msgs.append(f'Invalid hue_split: {hue_split}.')
    if not all([stats_var in STATS_VARS_TYPES for stats_var in stats_vars]):
        error_msgs.append(f'Invalid stats_vars: {stats_vars}.')

    if (boxplots or lineplots or stackedbarplots) and (box_day is None):
        error_msgs.append('Must specify box_day.')

    if normalization_type == FOLD_CHANGE_METHOD and statistical_test=='do_wilcoxon_test':
        error_msgs.append('Cannot do a Wilcoxon–Mann–Whitney test when using fold-change.')

    if not len(error_msgs) == 0:
        raise ValueError(" ".join(error_msgs))

    base_directories = [os.path.dirname(os.path.dirname(path)) for path in filepaths]
    if len(set(base_directories)) == 1:
        base_directory = base_directories[0]
    else:
        raise ValueError("Selected filepaths not all in same base directory")

    start_time = time.time()

    for path in filepaths:
        print('-----------------------------------')
        print('Processing file:', path)

        data = data_annotation.AnnotatedData([path])
        data.load_annotated_files()
        mi = data.dataframe

        if replicates == 'biological':
            mi['Total_total_normalized_norm_log2'] = mi['Total_total_normalized_norm_log2'].astype(float)
            mi['Total_relative_normalized_norm_log2'] = mi['Total_relative_normalized_norm_log2'].astype(float)
            mi['Total_total_fold_change_norm_log2_Control_DMSO'] = mi['Total_total_fold_change_norm_log2_Control_DMSO'].astype(float)
            mi['Total_relative_fold_change_norm_log2_Control_DMSO'] = mi['Total_relative_fold_change_norm_log2_Control_DMSO'].astype(float)

            mi=mi.groupby(['Day','Marker','Condition','Date'], sort=False, as_index=False).mean()

        start_day = data.start_day()
        end_day = data.end_day()
        frames = data.get_frames()
        if len(frames) == 1:
            frame = frames[0]
        else:
            #TODO: generalize code to handle this case
            raise ValueError("Input data has multiple frames in one file")

        if conditions_override and len(conditions_override) > 0:
            conditions = list(conditions_override)
        else:
            conditions = list(data.get_conditions())
        start_time_conditions = time.time()

        if (control_condition is None) or (control_condition == ""):
            control_condition = conditions[0]
        elif control_condition not in conditions:
            err = f'control_condition {control_condition} not contained in conditions for path {path}'
            raise ValueError(err)
        else:
            conditions.remove(control_condition)
            conditions.insert(0, control_condition)

        conditions_reduced=conditions.copy()
        conditions_reduced.remove(control_condition)

        for stats_var in stats_vars:
            #region intitialize print out
            start_time_stats = time.time()
            print('-----------------------------------')
            print('-----------------------------------')
            print('-----------------------------------')
            if stats_var=='Cell_percent':
                print('Processing Cell percentages')
            elif stats_var=='Total':
                print('Processing Total Cell counts')
            #end

            #endregion

            # set normalization is now taken care of in Create_Frame_mean_sheet.py
            # data.set_normalization(stats_var, control_condition)
            norm_colname = data.normalization_colname(normalization_type, data_scale, analyze_method, stats_var, control_condition)

            # data.save()

            # region Initilize for-loop parameters
            days_total=end_day-start_day+1
            days = [f'day{start_day}']
            for ijkl in range(start_day+1, end_day+1):
                days.append(f'day{ijkl}')


            if stats_var == 'Total':
                tt_p = np.ones(len(days))
                tt_c = np.zeros(len(days))
                tt_m = np.zeros(len(days))
                tt_all = np.zeros((3, len(days), len(conditions)))
            else:
                tt_p = np.ones((len(days), 3))
                tt_c = np.zeros((len(days), 3))
                tt_m = np.zeros((len(days), 3))
                tt_all = np.zeros((3, len(days), len(conditions), 3))

            if stats_var == 'Cell_percent':
                plot_type = "stacked_bar"  # box, violin, stacked_bar, line
            if stats_var == 'Total':
                plot_type = "line"  # box, violin, stacked_bar, line

            marker_list = ['RFP', 'YFP', 'Overlap']
            if stats_var == 'Total':
                marker = stats_var
            else:
                marker = 'all'

            # if x_var == "Day":
            #     graph_n =
            # else:
            #     graph_n = range(start_day,len(days)+start_day)
            graph_n = conditions
            # if hue_split == "Condition" and (plot_type != "stacked_bar" and plot_type != "line"):
            if (plot_type != "stacked_bar" and plot_type != "line"):
                graph_n = range(0, 1)

            # endregion

            #region do stats
            if do_stats:

                # region gameshowell
                if statistical_test=='do_gameshowell_test':
                    print('Producing Games-Howell Analysis results')

                    mi_gameshowell = mi.loc[mi['Condition'].isin(conditions)]
                    mi_gameshowell = mi_gameshowell[mi_gameshowell.Marker == 'RFP']

                    mi_gameshowell['sample_size_count'] = mi_gameshowell.groupby(by=['Condition', 'Day'])['Date'].transform('count')

                    gameshowell_frames = []
                    for day in range(mi['Day'].min()+1, mi['Day'].max() + 1):
                        m_day = mi_gameshowell[mi_gameshowell['Day'] == day]

                        df_gameshowell = pg.pairwise_gameshowell(m_day, norm_colname, 'Condition',effsize='none')

                        df_gameshowell['Day'] = day
                        df_gameshowell['reject_05'] = (df_gameshowell['pval'] < 0.05)
                        df_gameshowell['reject_01'] = (df_gameshowell['pval'] < 0.01)
                        df_gameshowell['reject_001'] = (df_gameshowell['pval'] < 0.001)

                        df_gameshowell['Sample_size_1'] = ''
                        df_gameshowell['Sample_size_2'] = ''

                        for con in conditions:
                            df_gameshowell.loc[df_gameshowell.A == con, 'Sample_size_1'] = np.max(
                                mi_gameshowell.loc[(mi_gameshowell.Condition == con) & (mi_gameshowell.Day == day),
                                             'sample_size_count'])
                            df_gameshowell.loc[df_gameshowell.B == con, 'Sample_size_2'] = np.max(
                                mi_gameshowell.loc[(mi_gameshowell.Condition == con) & (mi_gameshowell.Day == day),
                                             'sample_size_count'])

                            gameshowell_frames.append(df_gameshowell)

                    df_gameshowell = pd.concat(gameshowell_frames)

                    if save_excel_stats:
                        df_gameshowell.to_csv(
                            path_or_buf=os.path.join(base_directory, 'stats', f'gameshowell_results_{norm_colname}.csv'),
                            index=None,
                            header=True
                        )

                    # endregion

                #endregion

                #region tukey
                if statistical_test == 'do_tukey_test':
                    print('Producing Tukey Analysis results')

                    mi_tukey = mi.loc[mi['Condition'].isin(conditions)]
                    mi_tukey = mi_tukey[mi_tukey.Marker == 'RFP']

                    mi_tukey['sample_size_count']= mi_tukey.groupby(by=['Condition','Day'])['Date'].transform('count')
                    # print('sample_size_count', mi_tukey.columns, mi_tukey['Condition'], mi_tukey['sample_size_count'])

                    tukey_frames = []
                    Days_list = mi_tukey['Day'].to_numpy()
                    unique_Days = np.unique(Days_list)
                    # for j in range(0, len(unique_Days)):
                    for j in range(1, len(unique_Days)):
                        day=unique_Days[j]
                        m_day = mi_tukey[mi_tukey['Day'] == day]

                        result_05 = statsmodels.stats.multicomp.pairwise_tukeyhsd(
                            m_day[norm_colname], m_day['Condition'], alpha=0.05
                        )
                        df_tukey = pd.DataFrame(
                            data=result_05._results_table.data[1:],
                            columns=result_05._results_table.data[0]
                        )
                        df_tukey['Day'] = day
                        df_tukey['reject_05'] = (df_tukey['p-adj'] < 0.05)
                        df_tukey['reject_01'] = (df_tukey['p-adj'] < 0.01)
                        df_tukey['reject_001'] = (df_tukey['p-adj'] < 0.001)

                        df_tukey['Sample_size_1'] = ''
                        df_tukey['Sample_size_2'] = ''

                        for con in conditions:
                            df_tukey.loc[df_tukey.group1 == con,'Sample_size_1'] = np.max(mi_tukey.loc[(mi_tukey.Condition == con) & (mi_tukey.Day == day),
                                'sample_size_count'])
                            df_tukey.loc[df_tukey.group2 == con,'Sample_size_2'] = np.max(mi_tukey.loc[(mi_tukey.Condition == con) & (mi_tukey.Day == day),
                                'sample_size_count'])

                            tukey_frames.append(df_tukey)

                    df_tukey = pd.concat(tukey_frames)


                    if save_excel_stats:
                        df_tukey.to_csv(
                            path_or_buf=os.path.join(base_directory, 'stats', f'tukey_results_{norm_colname}.csv'),
                            index=None,
                            header=True
                        )

                #endregion
            #endregion


            # region Individual Conditions vs Control plots and stats


            for l, i in enumerate(graph_n): #graph_n is just the conditions list in the current iteration
                day = i
                print('Processing:',i, 'at frame',frame)

                # region  Titles and filenames
                # region  Titles and filenames

                # if x_var == "Day":
                #     ax_title = f'm{frame} {marker} {day}'
                    # if hue_split != "Condition":
                    #     ax_title = f'm{frame} {marker} {day}'
                ax_title = f'm{frame} {marker} {day}'
                    # else:
                    #     if plot_type == "stacked_bar":
                    #         ax_title = f'm{frame} {i}'
                    #     elif plot_type == "line":
                    #         ax_title = f'm{frame} {i} vs {control_condition}'
                    #     else:
                    #         ax_title = f'm{frame} {hue_choice[0]} vs {hue_choice[1]}'
                # else:
                #     ax_title = f'm{frame} {marker} Day {day}'

                data_dir = os.path.join(base_directory, 'data')
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                plots_dir = os.path.join(base_directory, 'plots')
                if not os.path.exists(plots_dir):
                    os.makedirs(plots_dir)
                stats_dir = os.path.join(base_directory, 'stats')
                if not os.path.exists(stats_dir):
                    os.makedirs(stats_dir)

                if plot_type == "violin":
                    # if hue_split == "Condition":
                    #     violin_dir = os.path.join(
                    #         base_directory, 'plots', 'violinplots', 'condition_1_vs_2',
                    #         f'{control_condition}_normalized', normalization_type, f'm{frame}'
                    #     )
                    #     if not os.path.exists(violin_dir):
                    #         os.makedirs(violin_dir)
                    #     plot_fname = os.path.join(violin_dir, f'{ax_title}.png')
                    violin_dir = os.path.join(
                        base_directory, 'plots', 'violinplots', 'condition_1_vs_2',
                        f'{control_condition}_normalized', normalization_type, f'm{frame}'
                    )
                    if not os.path.exists(violin_dir):
                        os.makedirs(violin_dir)
                    plot_fname = os.path.join(violin_dir, f'{ax_title}.png')
                    # else:
                    #     violin_dir = os.path.join(
                    #         base_directory, 'plots', 'violinplots',
                    #         f'{control_condition}_normalized', normalization_type, f'm{frame}'
                    #     )
                    #     if not os.path.exists(violin_dir):
                    #         os.makedirs(violin_dir)
                    #     plot_fname = os.path.join(violin_dir, f'{ax_title}.png')

                if boxplots:
                    box_dir = os.path.join(
                        base_directory, 'plots', 'boxplots',
                        f'{control_condition}_normalized',
                        normalization_type, f'm{frame}'
                    )
                    if not os.path.exists(box_dir):
                        os.makedirs(box_dir)
                    ax_title_boxplot = f'Day {box_day} Normalized Cell Counts Compared to {control_condition} - frame m{frame}'
                    boxplot_fname = os.path.join(box_dir, f'{control_condition} normalized {ax_title_boxplot}.png')

                if stackedbarplots:
                    stack_dir = os.path.join(
                        base_directory, 'plots', 'stackedbarplots',
                        f'{control_condition}_normalized', normalization_type, f'm{frame}'
                    )
                    if not os.path.exists(stack_dir):
                        os.makedirs(stack_dir)
                    ax_title_stackedbar = f'Day {box_day} Cell Cycle Proportions Compared to {control_condition} - frame m{frame}'
                    stackedbar_fname = os.path.join(
                        stack_dir, f'{control_condition} normalized {ax_title_stackedbar}.png'
                    )

                if lineplots:
                    line_dir = os.path.join(
                        base_directory, 'plots', 'lineplotsall',
                        f'{control_condition}_normalized',
                        normalization_type, f'm{frame}'
                    )
                    if not os.path.exists(line_dir):
                        os.makedirs(line_dir)
                    ax_title_line = f'Day {box_day} Normalized Cell Counts Compared to {control_condition} - frame m{frame}'
                    line_fname = os.path.join(line_dir, f'{control_condition} normalized {ax_title_line}.png')

                if plot_type == "stacked_bar":
                    stacked_bar_dir = os.path.join(
                        base_directory, 'plots', 'stacked_bar',
                        f'{control_condition}_normalized', normalization_type, f'm{frame}'
                    )
                    if not os.path.exists(stacked_bar_dir):
                        os.makedirs(stacked_bar_dir)
                    plot_fname =  os.path.join(stacked_bar_dir, f'{control_condition} normalized {ax_title}.png')

                if plot_type == "line":
                    line_dir = os.path.join(
                        base_directory, 'plots', 'lineplots',
                        f'{control_condition}_normalized',
                        normalization_type, f'm{frame}'
                    )
                    if not os.path.exists(line_dir):
                        os.makedirs(line_dir)
                    plot_fname = os.path.join(line_dir, f'{ax_title}.png')

                if colormap_plot:
                    colormap_dir = os.path.join(
                        base_directory, 'plots', 'colormaps',
                        f'{control_condition}_normalized',
                        normalization_type, f'm{frame}'
                    )
                    if not os.path.exists(colormap_dir):
                        os.makedirs(colormap_dir)

                    if statistical_test=='do_wilcoxon_test':
                        ax_title_colormap_p = f'{control_condition} normalized m{frame} Wilcoxon–Mann–Whitney test p-values'
                    else:
                        ax_title_colormap_p = f'{control_condition} normalized m{frame} ttest p-values'

                    fname_colormap_p = os.path.join(colormap_dir, f'{ax_title_colormap_p}.png')
                    ax_title_colormap_c = f'{control_condition} normalized m{frame} cohen\'s ds'
                    fname_colormap_c = os.path.join(colormap_dir, f'{ax_title_colormap_c}.png')
                    ax_title_colormap_m = f'{control_condition} normalized m{frame} mean differences'
                    fname_colormap_m = os.path.join(colormap_dir, f'{ax_title_colormap_m}.png')
                    ax_title_colormap_anova = f'{control_condition} normalized m{frame} anova p-values'
                    fname_colormap_anova = os.path.join(colormap_dir, f'{ax_title_colormap_anova}.png')

                    fnames_colormaps=[fname_colormap_p,fname_colormap_c,fname_colormap_m,fname_colormap_anova]
                # endregion

                #region stats part 2
                if do_stats:

                    # region ttest

                    if statistical_test=='do_ttest' or statistical_test=='do_wilcoxon_test':
                        mi_control = mi[mi['Condition'] == control_condition]
                        mi_drug = mi[mi['Condition'] == i]


                        if stats_var=='Cell_percent':
                            for iday in range (mi['Day'].min(),mi['Day'].max()+1):
                                mi_control_d= mi_control[mi_control['Day'] == iday]
                                mi_drug_d = mi_drug[mi_drug['Day'] == iday]

                                for k in range(0,3):
                                    mi_control_d_m = mi_control_d[mi_control_d['Marker'] == marker_list[k]]
                                    mi_drug_d_m  = mi_drug_d[mi_drug_d['Marker'] == marker_list[k]]

                                    if not iday == 0:
                                        if statistical_test=='do_wilcoxon_test':
                                            tt = stats.mannwhitneyu(mi_control_d_m[stats_var],mi_drug_d_m[stats_var])
                                        else:
                                            tt =stats.ttest_ind(mi_control_d_m[stats_var],mi_drug_d_m[stats_var])

                                        tt_p[iday-start_day,k]=tt[1]

                                    mean_control = np.mean(mi_control_d_m[stats_var])
                                    mean_drug = np.mean(mi_drug_d_m[stats_var])

                                    tt_m[iday-start_day,k] = mean_drug - mean_control

                                    std_control = np.std(mi_control_d_m[stats_var])
                                    std_drug = np.std(mi_drug_d_m[stats_var])

                                    cohen_d = abs((mean_control - mean_drug)) / np.sqrt(
                                        (np.square(std_control) + np.square(std_drug)) / 2)
                                    tt_c[iday-start_day,k]=cohen_d

                            tt_all[0,:,l]=tt_p
                            tt_all[1,:,l]=tt_c
                            tt_all[2,:,l]=tt_m

                        if stats_var=='Total':

                            mi_t = mi[mi['Condition'] == i]
                            mi_t = mi_t[mi_t['Marker'] == 'RFP']

                            mi_t_control = mi[mi['Condition'] == control_condition]
                            mi_t_control = mi_t_control[mi_t_control['Marker'] == 'RFP']

                            for day in range(mi['Day'].min(),mi['Day'].max()+1):

                                mi_control_d = mi_t_control[mi_t_control['Day'] == day]
                                mi_drug_d = mi_t[mi_t['Day'] == day]

                                if not day == 0:
                                    if statistical_test=='do_wilcoxon_test':
                                        tt = stats.mannwhitneyu(mi_control_d[norm_colname], mi_drug_d[norm_colname])
                                    else:
                                        tt = stats.ttest_ind(mi_control_d[norm_colname], mi_drug_d[norm_colname])

                                    tt_p[day-start_day] = tt[1]

                                mean_control = np.mean(mi_control_d[norm_colname])
                                mean_drug = np.mean(mi_drug_d[norm_colname])

                                if not mean_control == 0.0:
                                    tt_m[day-start_day] = (mean_drug - mean_control) / mean_control

                                std_control = np.std(mi_control_d[norm_colname])
                                std_drug = np.std(mi_drug_d[norm_colname])

                                if std_control == 0 and std_drug == 0:
                                    cohen_d = 0
                                else:
                                    cohen_d = abs((mean_control - mean_drug)) / np.sqrt(
                                        (np.square(std_control) + np.square(std_drug)) / 2)

                                tt_c[day-start_day] = cohen_d

                            tt_all[0,:,l]=tt_p
                            tt_all[1,:,l]=tt_c
                            tt_all[2,:,l]=tt_m

                    #endregion

                    #region anova
                    if statistical_test=='do_anova':
                        def eta_squared(aov):
                            aov['eta_sq'] = 'NaN'
                            aov['eta_sq'] = aov[:-1]['sum_sq'] / sum(aov['sum_sq'])
                            return aov
                        def omega_squared(aov):
                            mse = aov['sum_sq'][-1] / aov['df'][-1]
                            aov['omega_sq'] = 'NaN'
                            aov['omega_sq'] = (aov[:-1]['sum_sq'] - (aov[:-1]['df'] * mse)) / (sum(aov['sum_sq']) + mse)
                            return aov

                        mi_1 = mi[mi.Condition == control_condition]
                        mi_2 = mi[mi.Condition == i]
                        mi_an=pd.concat([mi_1,mi_2])

                        if stats_var == 'Total':
                            mi_an = mi_an[mi_an.Marker == marker_list[0]]
                            mi_an_base = mi_an[mi_an['Day'] == start_day]
                            mi_an_base = mi_an_base.reset_index(drop=True)

                            # formula = f'{norm_colname} ~ C({x_var}) + C(Condition) + C({x_var}):C(Condition)'
                            formula = f'{norm_colname} ~ C(Day) + C(Condition) + C(Day):C(Condition)'
                            model = ols(formula, mi_an).fit()
                            aov_table = anova_lm(model, type=2)

                            eta_squared(aov_table)
                            omega_squared(aov_table)

                            aov_table.insert(0, 'Drug', i)

                            if  l == 0:
                                aov_table_mark = aov_table
                            else:
                                aov_table_mark = aov_table_mark.append(aov_table)

                        if stats_var == 'Cell_percent':
                            for mark in marker_list:
                                mi_an_mark = mi_an[mi_an.Marker == mark]
                                formula = f'{stats_var} ~ C(Day) + C(Condition) + C(Day):C(Condition)'

                                model = ols(formula, mi_an_mark).fit()
                                aov_table = anova_lm(model, type=2)

                                aov_table.insert(0, 'Marker', mark)

                                eta_squared(aov_table)
                                omega_squared(aov_table)

                                aov_table.insert(0, 'Drug',i)

                                if mark==marker_list[0] and l==0:
                                    aov_table_mark=aov_table
                                else:
                                    aov_table_mark=aov_table_mark.append(aov_table)


                        if l==0:
                            aov_table_all=aov_table_mark
                        else:
                            aov_table_all=aov_table_mark.append(aov_table_mark)

                    #endregion

                #endregion

                #region individual plots
                if plots:
                    #region Global Seaborn parameters
                    sns.set(context=plot_context,font_scale=float(font_scale),style="whitegrid")
                    #endregion
                    if individual_plots:
                        print('Producing Individual Plots')

                        #region stacked bar
                        if plot_type=="stacked_bar":
                            mi_con = mi[mi['Condition'] == i]

                            mi_rfp = mi_con[mi_con['Marker'] == 'RFP']
                            mi_yfp = mi_con[mi_con['Marker'] == 'YFP']
                            mi_overlap = mi_con[mi_con['Marker'] == 'Overlap']
                            mi_new=pd.concat([mi_yfp,mi_overlap,mi_rfp])

                            mi_new['Marker'] = mi_new['Marker'].map({'RFP': 'G1', 'YFP': 'Late S,G2,M','Overlap':'Early S'})

                            means=mi_new.groupby(['Day','Marker'], sort=False).mean()
                            stds=mi_new.groupby(['Day','Marker'], sort=False).std()

                            ax = means.Cell_percent.unstack().plot(kind='bar',yerr=stds.Cell_percent.unstack(), stacked=True,
                                                                   capsize=5,color=['yellow','orange','red'], sort_columns=True)

                            handles, labels = ax.get_legend_handles_labels()
                            ax.legend(reversed(handles), reversed(labels), loc='upper right', bbox_to_anchor=(1.25, 0.8))
                            ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
                            ax.set_ylabel('Ratio')
                            ax.set_title(ax_title)

                            if statistical_test=='do_ttest':
                                Days_list = mi['Day'].to_numpy()
                                unique_Days=np.unique(Days_list)
                                for j in range(0,len(unique_Days)):
                                    m=0
                                    for k in range(0, 3):
                                        sum_means=means.iloc[j+k*days_total]['Cell_percent']
                                        m=m+sum_means
                                        if k==0:
                                            k_new=1
                                        if k==1:
                                            k_new=2
                                        if k==2:
                                            k_new=0
                                        if 0.01<=tt_p[unique_Days[j],k_new]<0.05:
                                            text(unique_Days[j]+0.05, m-0.05, '*' , fontsize=18)
                                        if 0.001<=tt_p[unique_Days[j],k_new]<0.01:
                                            text(unique_Days[j]+0.05, m-0.05, '**' , fontsize=18)
                                        if tt_p[unique_Days[j],k_new]<0.001:
                                            text(unique_Days[j]+0.05, m-0.05, '***' , fontsize=18)

                        #endregion

                        #region lineplots
                        if plot_type=="line":

                            mi_new = mi[(mi['Condition'] == i) & (mi['Marker'] == 'RFP')]
                            mi_control = mi[(mi['Condition'] == control_condition) & (mi['Marker'] == 'RFP')]
                            mi_new_both = mi_new.append(mi_control)

                            means = mi_new.groupby(['Day']).mean()
                            stds = mi_new.groupby(['Day']).std()

                            hue_choice = [control_condition, i]
                            # ax = sns.lineplot(x='Day', y=norm_colname, data=mi_new_both, hue=hue_split,hue_order=hue_choice,legend='full',
                            #                   ci='sd', palette = sns.color_palette("hsv", 2), style=hue_split, markers=True, dashes=True)
                            ax = sns.lineplot(x='Day', y=norm_colname, data=mi_new_both, hue='Condition',hue_order=hue_choice,legend='full',
                                              ci='sd', palette = sns.color_palette("hsv", 2), style='Condition', markers=True, dashes=True)

                            handles, labels = ax.get_legend_handles_labels()
                            ax.legend(handles, labels, loc='upper left')

                            x_days = np.arange(start_day, end_day+1)

                            plt.xticks(x_days)
                            ylabel = 'Normalized Cell Count'
                            ax.set_ylabel(ylabel)
                            ax.set_title(ax_title)

                            if statistical_test=='do_ttest':
                                Days_list = mi['Day'].to_numpy()
                                unique_Days=np.unique(Days_list)

                                for j in range(0,len(unique_Days)):
                                    m=means.iloc[j][norm_colname]
                                    if 0.01<=tt_p[unique_Days[j]]<0.05:
                                        text(unique_Days[j], m+0.05, '*' , fontsize=18 , horizontalalignment='center')
                                    if 0.001<=tt_p[unique_Days[j]]<0.01:
                                        text(unique_Days[j], m+0.05, '**' , fontsize=18 , horizontalalignment='center')
                                    if tt_p[unique_Days[j]]<0.001:
                                        text(unique_Days[j], m+0.05, '***' , fontsize=18 , horizontalalignment='center')


                        #endregion

                        #region Global plot parameters
                        ax.grid(False)

                        # if x_var=="Condition":
                        #     ax.set_xticklabels(ax.get_xticklabels(),rotation=30)

                        if marker!="all":
                            ax.set_title(ax_title)
                        if stats_var != 'Total':
                            ax.set(ylim=(0, 1.2))

                        fig = plt.gcf()
                        fig.set_size_inches(18,8)

                        if save_plots:
                            # plt.savefig(plot_fname)
                            plt.savefig(plot_fname, bbox_inches='tight')
                            plt.clf()
                            plt.close()
                        else:
                            plt.show()
                        #endregion

            #endregion

            #region save stats
            if save_excel_stats:
                print('Saving Stats')

                if statistical_test=='do_ttest':
                    if plot_type=="stacked_bar":
                        stats_dir= os.path.join(
                            base_directory, 'stats', f'{control_condition}_normalized', 
                            'percent_cell', f'm{frame}'
                        )
                        if not os.path.exists(stats_dir):
                            os.makedirs(stats_dir)
                        for n in range(0,3):
                            data_t_p=tt_all[0,:,:,n]
                            data_t_c=tt_all[1,:,:,n]
                            data_t_m=tt_all[2,:,:,n]
                            markers=['rfp','yfp','overlap']
                            ttest_pvalues = pd.DataFrame(data=data_t_p, index=days, columns=conditions)
                            ttest_cohens = pd.DataFrame(data=data_t_c, index=days,columns=conditions)
                            ttest_means = pd.DataFrame(data=data_t_m, index=days,columns=conditions)
                            ttest_pvalues.to_csv(
                                path_or_buf=os.path.join(stats_dir, f'ttests_pvalues_m{frame}_{markers[n]}.csv'),
                                index=None, header=True)
                            ttest_cohens.to_csv(
                                path_or_buf=os.path.join(stats_dir, f'ttests_cohens_m{frame}_{markers[n]}.csv'),
                                index=None, header=True)
                            ttest_means.to_csv(
                                path_or_buf=os.path.join(stats_dir, f'ttests_means_m{frame}_{markers[n]}.csv'),
                                index=None, header=True)

                    if plot_type == "line":
                        stats_dir=os.path.join(
                            base_directory, 'stats', f'{control_condition}_normalized', 
                            'total_cell_n', f'm{frame}'
                        )
                        if not os.path.exists(stats_dir):
                            os.makedirs(stats_dir)
                        data_t_p=tt_all[0]
                        data_t_c=tt_all[1]
                        data_t_m=tt_all[2]
                        ttest_pvalues = pd.DataFrame(data=data_t_p, index=days, columns=conditions)
                        ttest_cohens = pd.DataFrame(data=data_t_c, index=days, columns=conditions)
                        ttest_means = pd.DataFrame(data=data_t_m, index=days,columns=conditions)
                        ttest_pvalues.to_csv(path_or_buf=os.path.join(stats_dir, f'ttests_pvalues_m{frame}.csv'), index=None,header=True)  # Don't forget to add '.csv' at the end of the path
                        ttest_cohens.to_csv(path_or_buf=os.path.join(stats_dir, f'ttests_cohens_m{frame}.csv'), index=None,header=True)  # Don't forget to a' at the end of the path
                        ttest_means.to_csv(path_or_buf=os.path.join(stats_dir, f'ttests_means_m{frame}.csv'), index=None,header=True)  # Don't forget to a


                if statistical_test=='do_anova':

                    if plot_type == "line":
                        stats_dir=os.path.join(
                            base_directory, 'stats', f'{control_condition}_normalized', 
                            'total_cell_n', f'm{frame}'
                        )
                        if not os.path.exists(stats_dir):
                            os.makedirs(stats_dir)

                    if plot_type == "stacked_bar":
                        stats_dir= os.path.join(
                            base_directory, 'stats', f'{control_condition}_normalized', 
                            'percent_cell', f'm{frame}'
                        )
                        if not os.path.exists(stats_dir):
                            os.makedirs(stats_dir)

                    dir_fname= os.path.join(
                        stats_dir, f'anova_table_m{frame}.xls'
                    )

                    with pd.ExcelWriter(dir_fname) as writer:
                        aov_table_all.to_excel(writer)

            #endregion

            #region colormap plot
            if colormap_plot:
                print('Producing Combined Colormap plot')

                for fname in fnames_colormaps:
                    if stats_var == 'Total':
                        nn=1
                    else:
                        nn=3
                    n=0
                    fname_0=fname
                    myColors = ('black', 'blue', 'aqua', 'lime')
                    # myColors = ((0.8, 0.0, 0.0, 1.0), (0.0, 0.8, 0.0, 1.0), (0.0, 0.0, 0.8, 1.0), (0.0, 0.1, 0.1, 1.0))
                    if cmap_discrete:
                        cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))
                    else:
                        cmap = LinearSegmentedColormap.from_list('Custom', myColors, 100)

                    for n in range(0, nn):
                        if stats_var == 'Cell_percent':
                            data_t_p = tt_all[0, :, :, n]
                            data_t_c = tt_all[1, :, :, n]
                            data_t_m = tt_all[2, :, :, n]
                            markers = ['rfp', 'yfp', 'overlap']
                            fname =fname_0.replace('.png',f'_%{markers[n]}.png')

                        if stats_var == 'Total':
                            data_t_p = tt_all[0, :, :]
                            data_t_c = tt_all[1, :, :]
                            data_t_m = tt_all[2, :, :]
                            fname =fname_0.replace('.png','_n_cells.png')
                            # markers = ['rfp', 'yfp', 'overlap']

                        ttest_pvalues = pd.DataFrame(data=data_t_p, index=days, columns=conditions)
                        ttest_cohens = pd.DataFrame(data=data_t_c, index=days, columns=conditions)
                        ttest_means = pd.DataFrame(data=data_t_m, index=days, columns=conditions)

                        if fname_0==fnames_colormaps[0]:
                            if cmap_discrete:
                                arr = ttest_pvalues.to_numpy()
                                arr_shape = arr.shape
                                arr_new = np.zeros(arr_shape)

                                for i in range(arr_shape[0]):
                                    for j in range(arr_shape[1]):
                                        if 0.05 <= arr[i, j]:
                                            arr_new[i, j] = 0
                                        if 0.01 <= arr[i, j] < 0.05:
                                            arr_new[i, j] = 1
                                        if 0.001 <= arr[i, j] < 0.01:
                                            arr_new[i, j] = 2
                                        if arr[i, j] < 0.001:
                                            arr_new[i, j] = 3

                                ttest_pvalues = pd.DataFrame(data=arr_new, columns=ttest_pvalues.columns, index=ttest_pvalues.index)
                                c_pos = [0 + 0.375, 1 + 0.125, 2 - 0.125, 3 - 0.375]
                                position_labels = [ '     (p>0.05)', '*    (p<0.05)', '**   (p<0.01)','*** (p<0.001)']

                                ax = sns.heatmap(ttest_pvalues, cmap=cmap, linewidths=.5, linecolor='lightgray', vmin=0, vmax=3)
                            else:
                                c_pos = [0.006875 , 0.006875*3 ,0.006875*5 ,0.006875*7]
                                ax = sns.heatmap(ttest_pvalues, cmap=cmap, linewidths=.5, linecolor='lightgray', vmin=0, vmax=0.055)
                            ax_title=ax_title_colormap_p

                        if fname_0==fnames_colormaps[1]:
                            if cmap_discrete:
                                arr = ttest_cohens.to_numpy()
                                arr_shape = arr.shape
                                arr_new = np.zeros(arr_shape)

                                for i in range(arr_shape[0]):
                                    for j in range(arr_shape[1]):
                                        if 0.8 <= arr[i, j]:
                                            arr_new[i, j] = 3
                                        if 0.5 <= arr[i, j] < 0.8:
                                            arr_new[i, j] = 2
                                        if 0.2 <= arr[i, j] < 0.5:
                                            arr_new[i, j] = 1
                                        if arr[i, j] < 0.2:
                                            arr_new[i, j] = 0

                                ttest_cohens = pd.DataFrame(data=arr_new, columns=ttest_cohens.columns,
                                                             index=ttest_cohens.index)

                                c_pos=[0+0.375, 1+0.125, 2-0.125, 3-0.375]
                                position_labels = [ 'very small (cohen\'s d<0.2)', 'small (cohen\'s d>0.2)', 'medium (cohen\'s d>0.5)','large (cohen\'s d>0.8)']

                                ax = sns.heatmap(ttest_cohens, cmap=cmap, linewidths=.5, linecolor='lightgray', vmin=0, vmax=3)
                            else:
                                c_pos = [0.125, 0.125 * 3, 0.125 * 5, 0.125 * 7]
                                ax = sns.heatmap(ttest_cohens, cmap=cmap, linewidths=.5, linecolor='lightgray', vmin=0, vmax=1)
                            ax_title=ax_title_colormap_c

                        if fname_0==fnames_colormaps[2]:
                            myColors_diverging = ('red', 'white', 'blue')
                            # cmap_m = LinearSegmentedColormap.from_list('Custom', myColors, 100)
                            # cmap_m = sns.diverging_palette(240, 10, n=100)
                            cmap_m = LinearSegmentedColormap.from_list('Custom', myColors_diverging, 100)
                            if stats_var == 'Cell_percent':
                                ax = sns.heatmap(ttest_means, cmap=cmap_m, linewidths=.5, linecolor='lightgray', vmin=-0.4, vmax=0.4)
                            if stats_var == 'Total':
                                ax = sns.heatmap(ttest_means, cmap=cmap_m, linewidths=.5, linecolor='lightgray', vmin=-0.4, vmax=0.4)
                            ax_title=ax_title_colormap_m

                        an_len=int(len(aov_table_all))
                        aov_table_all_half=aov_table_all.iloc[0:(int(an_len/2))]
                        if fname_0==fnames_colormaps[3]:

                            if stats_var == 'Cell_percent':
                                aov_table_all_0=aov_table_all_half[aov_table_all_half.Marker==marker_list[n]]
                            if stats_var == 'Total':
                                aov_table_all_0=aov_table_all_half
                            aov_table_all_0=aov_table_all_0['PR(>F)']
                            aov_table_all_1=pd.DataFrame(index=conditions,columns=['C(Day)'], data=aov_table_all_0['C(Day)'].values)
                            aov_table_all_1=aov_table_all_1.T
                            aov_table_all_2=pd.DataFrame(index=conditions,columns=['C(Condition)'], data=aov_table_all_0['C(Condition)'].values)
                            aov_table_all_2=aov_table_all_2.T
                            aov_table_all_3=pd.DataFrame(index=conditions,columns=['C(Day):C(Condition)'], data=aov_table_all_0['C(Day):C(Condition)'].values)
                            aov_table_all_3=aov_table_all_3.T
                            # aov_table_all_4=pd.DataFrame(index=conditions,columns=['Residual'], data=aov_table_all_0['Residual'].values)
                            # aov_table_all_4=aov_table_all_4.T

                            aov_table_all_p=pd.concat([aov_table_all_1,aov_table_all_2,aov_table_all_3])#,aov_table_all_4])
                            aov_table_all_p.columns=conditions

                            if cmap_discrete:
                                arr = aov_table_all_p.to_numpy()
                                arr_shape = arr.shape
                                arr_new = np.zeros(arr_shape)

                                for i in range(arr_shape[0]):
                                    for j in range(arr_shape[1]):
                                        if 0.05 <= arr[i, j]:
                                            arr_new[i, j] = 0
                                        if 0.01 <= arr[i, j] < 0.05:
                                            arr_new[i, j] = 1
                                        if 0.001 <= arr[i, j] < 0.01:
                                            arr_new[i, j] = 2
                                        if 0 < arr[i, j] < 0.001:
                                            arr_new[i, j] = 3
                                        if np.isnan(arr[i, j]):
                                            arr_new[i, j] = float('NaN')

                                aov_table_all_p = pd.DataFrame(data=arr_new, columns=aov_table_all_p.columns, index=aov_table_all_p.index)
                                c_pos=[0+0.375, 1+0.125, 2-0.125, 3-0.375]
                                position_labels = [ '     (p>0.05)', '*    (p<0.05)', '**   (p<0.01)','*** (p<0.001)']

                                ax = sns.heatmap(aov_table_all_p, cmap=cmap, linewidths=.5, linecolor='lightgray', vmin=0, vmax=3)
                            else:
                                c_pos = [0.006875 , 0.006875*3 ,0.006875*5 ,0.006875*7]
                                ax = sns.heatmap(aov_table_all_p, cmap=cmap, linewidths=.5, linecolor='lightgray', vmin=0, vmax=0.055)
                            ax_title=ax_title_colormap_anova

                        # region Global plot parameters
                        ax.grid(False)
                        ax.invert_yaxis()

                        # ax.set(ylim=(0, 1.2))

                        fig = plt.gcf()
                        fig.set_size_inches(36, 20)
                        plt.gcf().subplots_adjust(bottom=0.2)

                        # ax.set_xticklabels(conditions, rotation=90)
                        # ax.set(xticks=ttest_pvalues.columns, rotation=90)
                        tick_list=np.r_[0:len(conditions)]+1
                        ax.set_xticks(tick_list)
                        ax.set_xticklabels(conditions, rotation=45)#, rotation_mode="anchor")
                        for tick in ax.xaxis.get_majorticklabels():
                            tick.set_horizontalalignment("right")
                        if fname_0==fnames_colormaps[3]:
                            ax.set_ylabel('Source of Variation')
                        else:
                            ax.set_ylabel('Days')
                        ax.set_xlabel('Conditions')

                        ax.xaxis.set_ticks_position('none')
                        ax.yaxis.set_ticks_position('none')
                        ax.tick_params(direction='in')
                        colorbar = ax.collections[0].colorbar
                        if cmap_discrete and not fname_0==fnames_colormaps[2]:
                            colorbar.set_ticks(c_pos)
                            colorbar.set_ticklabels(position_labels)
                        if fname_0==fnames_colormaps[0]:
                            colorbar.set_label('p-value')
                        if fname_0==fnames_colormaps[1]:
                            colorbar.set_label('cohen\'s d')
                        if fname_0==fnames_colormaps[2]:
                            colorbar.set_label('mean (Drug) - mean (Control) \n ----------------------------------------- \n  mean (Control)')
                        if fname_0==fnames_colormaps[3]:
                            colorbar.set_label('p-value')

                        if stats_var == 'Cell_percent':
                            ax.set_title(f'{ax_title} - %{markers[n]}')
                        else:
                            ax.set_title(f'{ax_title} n cells')

                        n = n + 1

                        if save_plots:
                            plt.savefig(fname)
                            plt.clf()
                            plt.close()
                        else:
                            plt.show()
                        # endregion

            #endregion

            #region boxplots all
            if boxplots:
                print('Producing Combined Boxplot')

                if stats_var=='Total':
                    mi_box=mi
                    mi_box = mi_box[mi_box.Marker == marker_list[0]]

                    mi_box=mi_box.loc[mi_box['Condition'].isin(conditions)]
                    sorterIndex = dict(zip(conditions, range(len(conditions))))

                    # Generate a rank column that will be used to sort
                    # the dataframe numerically

                    if replicates == 'technical':
                        mi_box['Condition_Rank'] = mi_box['Condition'].map(sorterIndex)
                        mi_box.sort_values(['Condition_Rank','WellNum'], ascending = [True,True], inplace = True)
                        mi_box.drop('Condition_Rank', 1, inplace=True)

                        swarmplot_size=8

                    else:
                        swarmplot_size=12


                    mi_box = mi_box[mi_box.Day == box_day]
                    mi_box = mi_box.reset_index(drop=True)


                    if analyze_method=='fold_change':
                        mi_box=mi_box.loc[mi_box.Condition!=control_condition]
                        mi_box = mi_box.reset_index(drop=True)

                    swarmplot_offset = 0  # offset to left of boxplot

                    # ax = sns.swarmplot(x="Condition", y=norm_colname, data=mi_box, hue="Date", size=swarmplot_size,
                    #                    edgecolor="white", linewidth=1, dodge=True)
                    g = mi_box.groupby(by=["Condition"])[norm_colname].median()

                    my_order=g.nlargest(len(g))
                    my_order=my_order.index.tolist()

                    ax = sns.swarmplot(x="Condition", y=norm_colname, data=mi_box, size=swarmplot_size, order=my_order,
                                       edgecolor="white", linewidth=1, dodge=True)

                    path_collections = [child for child in ax.get_children()
                                        if isinstance(child, matplotlib.collections.PathCollection)]

                    for path_collection in path_collections:
                        x, y = np.array(path_collection.get_offsets()).T
                        xnew = x + swarmplot_offset
                        offsets = list(zip(xnew, y))
                        path_collection.set_offsets(offsets)

                    ax = sns.boxplot(x="Condition", y=norm_colname, data=mi_box, order=my_order, linewidth=2, fliersize=0)
                    # ax = sns.swarmplot(x="Condition", y=norm_colname, data=mi_box, hue='Date', size=15, color='#767676',edgecolor="white",linewidth=1)
                    # ax = sns.swarmplot(x="Condition", y=norm_colname, data=mi_box, hue="Date", size=swarmplot_size,
                    #                    edgecolor="white", linewidth=1, dodge=True)

                    # custom_lines = [Line2D([0], [0], color="#5fa2ce", lw=4),
                    #                 Line2D([0], [0], color="#ffbc79", lw=4),
                    #                 Line2D([0], [0], color="#fc7d0b", lw=4),
                    #                 Line2D([0], [0], color="#c85200", lw=4),
                    #                 Line2D([0], [0], color="#1170aa", lw=4)]
                    # ax.legend(custom_lines,
                    #           ['-Control', '+Control', 'Novel Combo', 'Novel Repurposed', 'Published \nor In Use'],
                    #           loc='upper left', bbox_to_anchor=(0.14, 0.98))


                    if save_excel_stats:
                        means_box = m_day.groupby(['Condition'], sort=False).mean()
                        means_box.pop('Cell_percent')
                        means_box.pop('Count')
                        # means_box.pop('Frame')
                        # means_box.pop('Percent')
                        # means_box.pop('Day')
                        # means_box.pop('PlateNum')
                        # means_box.pop('WellNum')

                        # stds_box = m_day.groupby(['Condition'], sort=False).std()
                        stds_box = m_day.groupby(['Condition'], sort=False).std()
                        stds_box.pop('Cell_percent')
                        stds_box.pop('Count')
                        # stds_box.pop('Frame')
                        # stds_box.pop('Percent')
                        # stds_box.pop('Day')
                        # stds_box.pop('PlateNum')
                        # stds_box.pop('WellNum')

                        means_box.to_csv(
                            path_or_buf=os.path.join(stats_dir, f'Means_results_{analyze_method}_day_5.csv'), 
                            index=True,
                            header=True
                        )
                        stds_box.to_csv(
                            path_or_buf=os.path.join(stats_dir, f'Stds_results_{analyze_method}_day_5.csv'),
                            index=True,
                            header=True
                        )

                    if statistical_test=='do_tukey_test':
                        if sorterIndex[control_condition] != 0:
                            raise ValueError("control_condition is not the first condition, violating assumptions necessary for plotting")

                        for condition, iii in sorterIndex.items():
                            if condition == control_condition:
                                continue
                            query_str = f'Day == {box_day} & \
                                ((group1 == "{condition}" & group2 == "{control_condition}") | \
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
                            # every 4th line at the interval of 6 is median line
                            # 0 -> p25 1 -> p75 2 -> lower whisker 3 -> upper whisker 4 -> p50 5 -> upper extreme value

                            if analyze_method=='fold_change':
                                y = round(lines[3 + (iii-1) * 6].get_ydata()[0], 1)
                            else:
                                y = round(lines[3 + iii * 6].get_ydata()[0], 1)
                            # if analyze_method=='fold_change':
                            #     if reject_001:
                            #         text((iii-1) - 0.15, y + 0.7, '***', fontsize=40, color='black')
                            #     elif reject_01:
                            #         text((iii-1) - 0.1, y + 0.7, '**', fontsize=40, color='black')
                            #     elif reject_05:
                            #         text((iii-1) - 0.05, y + 0.7, '*', fontsize=40, color='black')
                            # else:
                            if not analyze_method == 'fold_change':
                                if reject_001:
                                    text(iii - 0.15, y + 0.7, '***', fontsize=40, color='black')
                                elif reject_01:
                                    text(iii - 0.1, y + 0.7, '**', fontsize=40, color='black')
                                elif reject_05:
                                    text(iii - 0.05, y + 0.7, '*', fontsize=40, color='black')


                    ax.grid(True)
                    bottom, top = ax.get_ylim()
                    if analyze_method == "fold_change":
                        ax.set(ylim=(bottom-0.2*np.abs(bottom), 0.1))
                    else:
                        ax.set(ylim=(bottom-0.2*np.abs(bottom), top+0.2*np.abs(top)))
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

                    if len(conditions)<6:
                        rotation=0
                        tick_orientation='center'
                    else:
                        rotation=37
                        tick_orientation='right'

                    # Con_list = mi_box['Condition'].to_numpy()
                    # con_list = np.unique(Con_list)
                    # con_list = con_list.tolist()

                    con_list = [item.get_text() for item in ax.get_xticklabels()]

                    conditions_labels = [w.replace('_', ' ') for w in con_list]

                    if len(conditions)<15:
                        breakline='\n'
                    else:
                        breakline = ''

                    conditions_labels = [w.replace('uM', 'μM'+breakline) for w in conditions_labels]
                    conditions_labels = [w.replace('nM', 'nM'+breakline) for w in conditions_labels]
                    conditions_labels = [w.replace('mM', 'mM'+breakline) for w in conditions_labels]

                    # conditions_label_reduced = [w.replace('_', ' \n ') for w in conditions_reduced]
                    # conditions_label_reduced = [w.replace('uM', 'μM') for w in conditions_label_reduced]

                    ax.set_xticklabels(conditions_labels, rotation=rotation,
                                       ha=tick_orientation)  # , rotation_mode="anchor")
                    if analyze_method == "fold_change":
                        # ax.set_xticklabels(conditions_label_reduced, rotation=rotation, ha=tick_orientation)  # , rotation_mode="anchor")
                        ax.set_ylabel('Log2 (fold change)')
                        plt.axhline(y=0)
                    else:
                        ax.set_xticklabels(conditions_labels, rotation=rotation, ha=tick_orientation)  # , rotation_mode="anchor")
                    # for tick in ax.xaxis.get_majorticklabels():
                    #     tick.set_horizontalalignment("right")
                        ax.set_ylabel('Normalized Cell Counts')
                    # ax.set_xlabel('Conditions')
                    ax.set_xlabel('')

                    # ax.set_title(ax_title_boxplot)
                    ax.set_title('')

                    ax.xaxis.set_ticks_position('none')
                    ax.yaxis.set_ticks_position('none')
                    ax.tick_params(direction='in')


                    if save_plots:
                        plt.savefig(boxplot_fname)
                        plt.clf()
                        plt.close()
                    else:
                        plt.show()
                    # endregion

            #endregion

            #region stackedbarplots all
            if stackedbarplots:
                print('Producing Combined Stackedbarplot')
                # matplotlib.rc('xtick', labelsize=8)
                if stats_var == 'Cell_percent':
                    # mi_rfp = mi_con[mi_con['Marker'] == 'RFP']
                    # mi_yfp = mi_con[mi_con['Marker'] == 'YFP']
                    # mi_overlap = mi_con[mi_con['Marker'] == 'Overlap']
                    # mi_new = pd.concat([mi_yfp, mi_overlap, mi_rfp])
                    mi_new2 = mi[mi['Day'] == box_day]


                    mi_new2 = mi_new2.loc[mi_new2['Condition'].isin(conditions)]


                    sorterIndex1 = dict(zip(conditions, range(len(conditions))))
                    mi_new2['Condition_Rank'] = mi_new2['Condition'].map(sorterIndex1)
                    sorterIndex2 = dict(zip(['RFP','Overlap','YFP'], range(len(['RFP','Overlap','YFP']))))
                    mi_new2['Marker_Rank'] = mi_new2['Marker'].map(sorterIndex2)
                    mi_new2.sort_values(['Condition_Rank','Marker_Rank'], ascending=[True,False], inplace=True)
                    mi_new2.drop('Condition_Rank', 1, inplace=True)
                    mi_new2.drop('Marker_Rank', 1, inplace=True)

                    mi_new2['Marker'] = mi_new2['Marker'].map(
                        {'RFP': 'G1', 'YFP': 'Late S,G2,M', 'Overlap': 'Early S'})

                    mi_box = mi
                    mi_box = mi_box[mi_box.Marker == marker_list[0]]

                    mi_box = mi_box.loc[mi_box['Condition'].isin(conditions)]

                    mi_box = mi_box[mi_box.Day == box_day]
                    mi_box = mi_box.reset_index(drop=True)

                    g = mi_box.groupby(by=["Condition"])['Total_total_fold_change_norm_log2_Control_DMSO'].median()

                    my_order = g.nlargest(len(g))
                    my_order = my_order.index.tolist()

                    sorterIndex = dict(zip(my_order, range(len(my_order))))
                    mi_new2['Condition_rank'] = mi_new2['Condition'].map(sorterIndex)

                    my_order2 = ['Late S,G2,M', 'Early S','G1']
                    sorterIndex2 = dict(zip(my_order2, range(len(my_order2))))
                    mi_new2['Marker_rank'] = mi_new2['Marker'].map(sorterIndex2)

                    mi_new2.sort_values(['Condition_rank','Marker_rank'],
                                        ascending=[True,True], inplace=True)
                    mi_new2.drop('Condition_rank', 1, inplace=True)
                    mi_new2.drop('Marker_rank', 1, inplace=True)


                    means = mi_new2.groupby(['Condition', 'Marker'], sort=False).mean()
                    stds = mi_new2.groupby(['Condition', 'Marker'], sort=False).std()

                    ax = means.Cell_percent.unstack().plot(kind='bar', yerr=stds.Cell_percent.unstack(),
                                                           stacked=True,
                                                           capsize=5, color=['yellow', 'orange', 'red'],
                                                           sort_columns=False)

                    handles, labels = ax.get_legend_handles_labels()
                    # box = ax.get_position()
                    # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                    ax.legend(reversed(handles), reversed(labels), loc='upper right', bbox_to_anchor=(1.2, 0.8))

                    con_list = [item.get_text() for item in ax.get_xticklabels()]

                    conditions_labels = [w.replace('_', ' ') for w in con_list]
                    conditions_labels = [w.replace('per', '%') for w in conditions_labels]

                    if len(conditions) < 15:
                        breakline = '\n'
                        rotation = 37
                        tick_orientation = 'center'
                    else:
                        breakline = ''
                        rotation = 37
                        tick_orientation = 'right'

                    conditions_labels = [w.replace('uM', 'μM' + breakline) for w in conditions_labels]
                    conditions_labels = [w.replace('nM', 'nM' + breakline) for w in conditions_labels]
                    conditions_labels = [w.replace('mM', 'mM' + breakline) for w in conditions_labels]

                    ax.set_xticklabels(conditions_labels, rotation=rotation,
                                       ha=tick_orientation)  # , rotation_mode="anchor")

                    ax.set_ylabel('Ratio')

                    ax.grid(True)
                    # ax.set(ylim=(0, 1.2))
                    fig = plt.gcf()
                    fig.set_size_inches(20, 10)
                    plt.gcf().subplots_adjust(bottom=0.4)
                    plt.gcf().subplots_adjust(right=0.85)
                    ax.set_xlabel('')

                    # ax.set_xticklabels(conditions, rotation=90)
                    # ax.set(xticks=ttest_pvalues.columns, rotation=90)
                    tick_list = np.r_[0:len(conditions)]
                    ax.set_xticks(tick_list)
                    # print(conditions)
                    # ax.set_xticklabels(conditions, rotation=37, ha='right')  # , rotation_mode="anchor")
                    for tick in ax.xaxis.get_majorticklabels():
                        tick.set_horizontalalignment("right")


                    # ax.set_title(ax_title_stackedbar)
                    ax.set_title('')

                    if statistical_test=='do_ttest':
                        j=box_day
                        m = 0
                        for con_bar in range(0,len(conditions)):
                            for k in range(0, 3):
                                sum_means = means.iloc[3*con_bar+k]['Cell_percent']
                                # sum_means = means.iloc[j - start_day + k * days_total]['Cell_percent']
                                m = m + sum_means
                                if k == 0:
                                    k_new = 1
                                if k == 1:
                                    k_new = 2
                                if k == 2:
                                    k_new = 0

                                if 0.01 <= tt_all[0, j - start_day, con_bar,k_new] < 0.05:
                                    text(con_bar + 0.05, m - 0.05, '*', fontsize=18)
                                if 0.001 <= tt_all[0, j - start_day, con_bar,k_new] < 0.01:
                                    text(con_bar + 0.05, m - 0.05, '**', fontsize=18)
                                if tt_all[0, j - start_day, con_bar,k_new] < 0.001:
                                    text(con_bar + 0.05, m - 0.05, '***', fontsize=18)
                            m = 0



                    if save_plots:
                        plt.savefig(stackedbar_fname)
                        plt.clf()
                        plt.close()
                    else:
                        plt.show()

            # endregion all

            # region lineplots all
            if lineplots:
                print('Producing Combined Lineplot')

                if stats_var == 'Total':
                    mi_box = mi
                    mi_box = mi_box[mi_box.Marker == marker_list[0]]

                    mi_box = mi_box.loc[mi_box['Condition'].isin(conditions)]
                    sorterIndex = dict(zip(conditions, range(len(conditions))))

                    # Generate a rank column that will be used to sort
                    # the dataframe numerically
                    mi_box['Condition_Rank'] = mi_box['Condition'].map(sorterIndex)
                    mi_box.sort_values(['Condition_Rank', 'WellNum'], ascending=[True, True], inplace=True)
                    mi_box.drop('Condition_Rank', 1, inplace=True)

                    ax = sns.lineplot(x='Day', y=norm_colname, data=mi_box, hue='Condition', linewidth=6,
                                      legend='full', ci=None)
                    handles, labels = ax.get_legend_handles_labels()
                    for legobj in handles:
                        legobj.set_linewidth(6.0)
                    vertical_line_label = 'Removal of Drug'
                    x0 = 6
                    plt.axvline(x0, color='black', linestyle='--', linewidth=3, label=vertical_line_label)

                    ax.grid(True)

                    x_days = np.arange(start_day, end_day + 1)
                    plt.xticks(x_days)

                    fig = plt.gcf()
                    fig.set_size_inches(20, 20)
                    box = ax.get_position()

                    plt.gcf().subplots_adjust(bottom=0.3)

                    ax.set_ylabel('Normalized Cell Counts')

                    ax.set_title(ax_title_line)

                    ax.xaxis.set_ticks_position('none')
                    ax.yaxis.set_ticks_position('none')
                    ax.tick_params(direction='in')

                    if save_plots:
                        plt.savefig(line_fname)
                        plt.clf()
                        plt.close()
                    else:
                        plt.show()
            # endregion

            print("Time spent on ", stats_var," in s: %s" % round((time.time() - start_time_stats), 2))

        print("Time spent on ", control_condition, " in s: %s" % round((time.time() - start_time_conditions), 2))

        data.save()

    print("Total time passed in s: %s" % round((time.time() - start_time), 2))


if __name__ == "__main__":
    filepaths = sys.argv[1:]

    stats_vars = ['Total', 'Cell_percent']
    # x_var = "Day"  # x_axis variable, mostly 'Day' right now for all major plots (line, stacked bar and colormap)

    control_condition = "Control_DMSO"

    normalization_type = RELATIVE_NORM

    data_scale = LOG2_SCALE

    analyze_method = NORMALIZED_METHOD

    replicates = TECHNICAL

    do_stats = True  # needed for plotting line and stacked bar plots with stars, as well as for colormaps
    statistical_test = GAMESHOWELL
    save_excel_stats = True  # True = saves stats to csv or xls files. needed for colormap-plots

    plots = True  # True = create plots
    colormap_plot = True  # create color map of stat results
    cmap_discrete = True  # True = discrete, False = continous
    individual_plots = True # create individual line and/or bar graph plots

    boxplots = True
    stackedbarplots = True
    lineplots = True
    box_day = 6

    save_plots = True  # True = save all plots,  or False = stops at each condition to show plot without saving it

    plot_context = 'talk'  # 'talk', 'poster', 'notebook' - use talk for now

    font_scale = 1.2  # 'talk', 'poster', 'notebook' - use talk for now

    # hue_split = "Condition"  # "Percent" or 'Condition'. mostly 'Condition' right now for all major plots (line, stacked bar and colormap)

    create_plots_and_stats(
        control_condition=control_condition,
        stats_vars=stats_vars,
        replicates=replicates,
        # x_var=x_var,
        filepaths=filepaths,
        normalization_type=normalization_type,
        data_scale=data_scale,
        analyze_method=analyze_method,
        do_stats=do_stats,
        save_excel_stats=save_excel_stats,
        plots=plots,
        colormap_plot=colormap_plot,
        cmap_discrete=cmap_discrete,
        individual_plots=individual_plots,
        boxplots=boxplots,
        stackedbarplots=stackedbarplots,
        lineplots=lineplots,
        box_day=box_day,
        save_plots=save_plots,
        plot_context=plot_context,
        font_scale=font_scale,
        # hue_split=hue_split
    )
