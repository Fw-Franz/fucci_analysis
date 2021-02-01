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
from fucci_analysis import data_annotation

NORMALIZATION_TYPES = ['total', 'relative']
STATS_VARS_TYPES = ['Cell_percent', 'Total']
X_VAR_TYPES = ['Day']
PLOT_CONTEXT_TYPES = ['talk', 'poster', 'notebook']
HUE_SPLIT_TYPES = ['Percent', 'Condition']


def create_plots_and_stats(stats_vars, x_var, filepaths, normalization_type,
        box_day, plot_context, hue_split,
        control_condition=None,
        plots=False, save_plots=False, colormap_plot=False, cmap_discrete=False,
        individual_plots=False, boxplots=False, stackedbarplots=False, lineplots=False,
        do_ttest=False, do_wilcoxon_test=False, do_anova=False,
        do_tukey_test=False, save_excel_stats=False):

    if normalization_type not in NORMALIZATION_TYPES:
        raise ValueError(f'Invalid normalization_type: {normalization_type}')
    if x_var not in X_VAR_TYPES:
        raise ValueError(f'Invalid x_var: {x_var}')
    if plot_context not in PLOT_CONTEXT_TYPES:
        raise ValueError(f'Invalid plot_context: {plot_context}')
    if hue_split not in HUE_SPLIT_TYPES:
        raise ValueError(f'Invalid hue_split: {hue_split}')
    if not all([stats_var in STATS_VARS_TYPES for stats_var in stats_vars]):
        raise ValueError(f'Invalid stats_vars: {stats_vars}')

    start_time = time.time()

    for path in filepaths:
        print('-----------------------------------')
        print('Processing file:', path)
        l = 0

        data = data_annotation.AnnotatedData([path])
        mi = data.dataframe
        start_day = data.start_day()
        end_day = data.end_day()
        frame = data.get_frame()
        conditions = data.get_conditions()
        start_time_conditions = time.time()

        if control_condition is None:
            control_condition = conditions[0]
        if control_condition not in conditions:
            raise ValueError(f'control_condition {control_condition} not contained in conditions for path {path}')
        print(control_condition)

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

            if x_var == "Day":
                graph_n = conditions
            else:
                graph_n = range(start_day,len(days)+start_day)
            if hue_split == "Condition" and (plot_type != "stacked_bar" and plot_type != "line"):
                graph_n = range(0, 1)

            # endregion

            #region tukey
            if do_tukey_test:

                mi_tukey = mi.loc[mi['Condition'].isin(conditions)]
                mi_tukey = mi_tukey[mi_tukey.Marker == 'RFP']

                mi_tukey['norm'] = 0.

                mi_tukey = mi_tukey.reset_index(drop=True)

                mi_base = mi_tukey[mi_tukey['Day'] == start_day]
                mi_base = mi_base.reset_index(drop=True)

                for day in range(mi['Day'].min(), mi['Day'].max() + 1):
                    m_day = mi_tukey[mi_tukey['Day'] == day]
                    ind = m_day.index
                    m_day = m_day.reset_index(drop=True)

                    if normalization_type == 'relative':
                        m_day['norm'] = (m_day[stats_var] - mi_base[stats_var]) / mi_base[stats_var]
                    else:
                        m_day['norm'] = (m_day[stats_var]) / mi_base[stats_var]

                    result_05 = statsmodels.stats.multicomp.pairwise_tukeyhsd(m_day[stats_var], m_day['Condition'],
                                                                              alpha=0.05)
                    result_01 = statsmodels.stats.multicomp.pairwise_tukeyhsd(m_day[stats_var], m_day['Condition'],
                                                                              alpha=0.01)
                    result_001 = statsmodels.stats.multicomp.pairwise_tukeyhsd(m_day[stats_var], m_day['Condition'],
                                                                           alpha=0.001)
                    # print(result.summary())
                    if day==start_day:
                        df_05 = pd.DataFrame(data=result_05._results_table.data[1:],
                                             columns=result_05._results_table.data[0])
                        df_05['Day']=day
                        df_01 = pd.DataFrame(data=result_01._results_table.data[1:],
                                             columns=result_01._results_table.data[0])
                        df_01['Day']=day
                        df_001 = pd.DataFrame(data=result_001._results_table.data[1:],
                                              columns=result_001._results_table.data[0])
                        df_001['Day']=day
                    else:
                        df_05_i=pd.DataFrame(data=result_05._results_table.data[1:],
                                     columns=result_05._results_table.data[0])
                        df_05_i['Day']=day
                        df_05 = df_05.append(df_05_i)

                        df_01_i = pd.DataFrame(data=result_01._results_table.data[1:],
                                             columns=result_01._results_table.data[0])
                        df_01_i['Day'] = day
                        df_01 = df_01.append(df_01_i)

                        df_001_i = pd.DataFrame(data=result_001._results_table.data[1:],
                                              columns=result_001._results_table.data[0])
                        df_001_i['Day'] = day
                        df_001 = df_001.append(df_001_i)


                df_05.to_csv(path_or_buf=os.path.join(base_directory, 'stats', 'tukey_results_05.csv'),
                          index=None, header=True)

                df_01.to_csv(path_or_buf=os.path.join(base_directory, 'stats', 'tukey_results_01.csv'),
                          index=None, header=True)

                df_001.to_csv(path_or_buf=os.path.join(base_directory, 'stats', 'tukey_results_001.csv'),
                          index=None, header=True)

            #endregion

            for i in graph_n: #graph_n is just the conditions list in the current iteration
                day = i
                print('Processing:',i, 'at frame',frame)

                # region  Titles and filenames
                if x_var == "Day":
                    if hue_split != "Condition":
                        ax_title = f'm{frame} {marker} {day}'
                    else:
                        if plot_type == "stacked_bar":
                            ax_title = f'm{frame} {i}'
                        elif plot_type == "line":
                            ax_title = f'm{frame} {i} vs {control_condition}'
                        else:
                            ax_title = f'm{frame} {hue_choice[0]} vs {hue_choice[1]}'
                else:
                    ax_title = f'm{frame} {marker} Day {day}'

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
                    if hue_split == "Condition":
                        violin_dir = os.path.join(
                            base_directory, 'plots', 'violinplots', 'condition_1_vs_2',
                            f'{control_condition}_normalized', f'm{frame}'
                        )
                        if not os.path.exists(violin_dir):
                            os.makedirs(violin_dir)
                        plot_fname = os.path.join(violin_dir, f'{ax_title}.png')
                    else:
                        violin_dir = os.path.join(
                            base_directory, 'plots', 'violinplots',
                            f'{control_condition}_normalized', f'm{frame}'
                        )
                        if not os.path.exists(violin_dir):
                            os.makedirs(violin_dir)
                        plot_fname = os.path.join(violin_dir, f'{ax_title}.png')

                if boxplots:
                    box_dir = os.path.join(
                        base_directory, 'plots', 'boxplots',
                        f'{control_condition}_normalized',
                        f'm{frame}'
                    )
                    if not os.path.exists(box_dir):
                        os.makedirs(box_dir)
                    ax_title_boxplot = f'Day {box_day} Normalized Cell Counts Compared to {control_condition} - frame m{frame}'
                    boxplot_fname = os.path.join(box_dir, f'{control_condition} normalized {ax_title_boxplot}.png')

                if stackedbarplots:
                    stack_dir = os.path.join(
                        base_directory, 'plots', 'stackedbarplots',
                        f'{control_condition}_normalized', f'm{frame}'
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
                        f'm{frame}'
                    )
                    if not os.path.exists(line_dir):
                        os.makedirs(line_dir)
                    ax_title_line = f'Day {box_day} Normalized Cell Counts Compared to {control_condition} - frame m{frame}'
                    line_fname = os.path.join(line_dir, f'{control_condition} normalized {ax_title_line}.png')

                if plot_type == "stacked_bar":
                    stacked_bar_dir = os.path.join(
                        base_directory, 'plots', 'stacked_bar',
                        f'{control_condition}_normalized', f'm{frame}'
                    )
                    if not os.path.exists(stacked_bar_dir):
                        os.makedirs(stacked_bar_dir)
                    plot_fname =  os.path.join(stacked_bar_dir, f'{control_condition} normalized {ax_title}.png')

                if plot_type == "line":
                    line_dir = os.path.join(
                        base_directory, 'plots', 'lineplots',
                        f'{control_condition}_normalized',
                        f'm{frame}'
                    )
                    if not os.path.exists(line_dir):
                        os.makedirs(line_dir)
                    plot_fname = os.path.join(line_dir, f'{ax_title}.png')

                if colormap_plot:
                    colormap_dir = os.path.join(
                        base_directory, 'plots', 'colormaps',
                        f'{control_condition}_normalized', 
                        f'm{frame}'
                    )
                    if not os.path.exists(colormap_dir):
                        os.makedirs(colormap_dir)

                    if do_wilcoxon_test:
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

                #region stats
                #region ttest
                if do_ttest:
                    mi_control = mi_t[mi_t['Condition'] == control_condition]
                    mi_drug = mi_t[mi_t['Condition'] == i]


                    if stats_var=='Cell_percent':
                        for iday in range (mi['Day'].min(),mi['Day'].max()+1):
                            mi_control_d= mi_control[mi_control['Day'] == iday]
                            mi_drug_d = mi_drug[mi_drug['Day'] == iday]

                            for k in range(0,3):
                                mi_control_d_m = mi_control_d[mi_control_d['Marker'] == marker_list[k]]
                                mi_drug_d_m  = mi_drug_d[mi_drug_d['Marker'] == marker_list[k]]

                                if not iday == 0:
                                    if do_wilcoxon_test:
                                        tt = stats.mannwhitneyu(mi_control_d_m[stats_var],mi_drug_d_m[stats_var])
                                    else:
                                        tt =stats.ttest_ind(mi_control_d_m[stats_var],mi_drug_d_m[stats_var])

                                    tt_p[iday-start_day,k]=tt[1]


                                mi_control_d_m[stats_var] = pd.to_numeric(mi_control_d_m[stats_var])
                                mi_drug_d_m[stats_var] =pd.to_numeric(mi_drug_d_m[stats_var])

                                mean_drug1 = np.mean(mi_control_d_m[stats_var])
                                mean_drug2 = np.mean(mi_drug_d_m[stats_var])
                                # mean_drug1 = mi_control_d_m[stats_var].mean()
                                # mean_drug2 = mi_drug_d_m[stats_var].mean()

                                tt_m[iday-start_day,k] = mean_drug2 - mean_drug1

                                cohen_d = abs((mean_drug1 - mean_drug2)) / np.sqrt(
                                    (np.square(np.std(mi_control_d_m[stats_var])) + np.square(np.std(mi_drug_d_m[stats_var]))) / 2)
                                tt_c[iday-start_day,k]=cohen_d

                        tt_all[0,:,l]=tt_p
                        tt_all[1,:,l]=tt_c
                        tt_all[2,:,l]=tt_m

                    if stats_var=='Total':

                        mi_t = mi[mi['Condition'] == i]

                        mi_t = mi_t[mi_t['Marker'] == 'RFP']

                        mi_t['norm'] = 0.

                        mi_t = mi_t.reset_index(drop=True)

                        mi_t_base = mi_t[mi_t['Day'] == start_day]
                        mi_t_base = mi_t_base.reset_index(drop=True)

                        for day in range(mi['Day'].min(),mi['Day'].max()+1):
                            m_day = mi_t[mi_t['Day'] == day]
                            ind = m_day.index
                            m_day = m_day.reset_index(drop=True)
                            if normalization_type == 'relative':
                                m_day['norm'] = (m_day[stats_var] - mi_t_base[stats_var]) / mi_t_base[stats_var]
                            else:
                                m_day['norm'] = (m_day[stats_var]) / mi_t_base[stats_var]
                            k = 0
                            for j in ind:
                                mi_t['norm'].iloc[j] = m_day['norm'].iat[k]
                                k = k + 1

                        if i==control_condition:
                            mi_t_control=mi_t


                        # print('mi_t_control[norm]', mi_t_control['norm'])
                        # print('mi_t[norm]', mi_t['norm'])

                        for day in range(mi['Day'].min(),mi['Day'].max()+1):

                            mi_control_d = mi_t_control[mi_t_control['Day'] == day]
                            mi_drug_d = mi_t[mi_t['Day'] == day]

                            # print('mi_control_d[norm]', mi_control_d['norm'])
                            # print('mi_drug_d[norm]', mi_drug_d['norm'])
                            # if not i == control_condition:
                            if not day == 0:
                                if do_wilcoxon_test:
                                    tt = stats.mannwhitneyu(mi_control_d['norm'], mi_drug_d['norm'])
                                else:
                                    tt = stats.ttest_ind(mi_control_d['norm'], mi_drug_d['norm'])

                                tt_p[day-start_day] = tt[1]


                            # print(mi_control_d['norm'])
                            # print(type(mi_drug_d['norm']))

                            mean_drug1 = np.mean(mi_control_d['norm'])
                            mean_drug2 = np.mean(mi_drug_d['norm'])

                            # print(mean_drug1,mean_drug2)
                            if normalization_type == 'total':
                                tt_m[day-start_day] = (mean_drug2 - mean_drug1)/mean_drug1


                            cohen_d = abs((mean_drug1 - mean_drug2)) / np.sqrt(
                                (np.square(np.std(mi_control_d['norm'])) + np.square(
                                    np.std(mi_drug_d['norm']))) / 2)
                        # print("cohen's d: ", cohen_d)
                            tt_c[day-start_day] = cohen_d

                        tt_all[0,:,l]=tt_p
                        tt_all[1,:,l]=tt_c
                        if normalization_type == 'total':
                            tt_all[2,:,l]=tt_m

                    # print('t_final:',tt_p,tt_c)

                    # slope, intercept, r_value, p_value, std_err = stats.linregress(mi_fixed[stats_var], mi_random[stats_var])
                    # print("r^2: ", r_value ** 2)

                    #endregion

                    #region anova
                    if do_anova:
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

                            mi_an['norm'] = 0.

                            mi_an = mi_an.reset_index(drop=True)

                            mi_an_base = mi_an[mi_an['Day'] == start_day]
                            mi_an_base = mi_an_base.reset_index(drop=True)

                            for day in range(mi['Day'].min(),mi['Day'].max()+1):
                                m_day = mi_an[mi_an['Day'] == day]
                                ind = m_day.index
                                m_day = m_day.reset_index(drop=True)

                                if normalization_type == 'relative':
                                    m_day['norm'] = (m_day[stats_var]  - mi_an_base[stats_var]) / mi_an_base[stats_var]
                                else:
                                    m_day['norm'] = (m_day[stats_var]) / mi_an_base[stats_var]

                                k = 0
                                for j in ind:
                                    mi_an['norm'].iloc[j] = m_day['norm'].iat[k]
                                    k = k + 1

                            formula = f'norm ~ C({x_var}) + C(Condition) + C({x_var}):C(Condition)'
                            # print("2 way AnoVa formula: ",formula)
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
                                formula = f'{stats_var} ~ C({x_var}) + C(Condition) + C({x_var}):C(Condition)'

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


                #region individual plots
                if plots:
                    #region Global Seaborn parameters
                    sns.set(context=plot_context,font_scale=1.5,style="whitegrid")
                    #endregion
                    if individual_plots:

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

                            if do_ttest:
                                for j in range(mi['Day'].min(),mi['Day'].max()+1):
                                #     mi_control_d = mi_control[mi_control['Day'] == j]
                                #     mi_drug_d = mi_drug[mi_drug['Day'] == j]
                                    m=0
                                    for k in range(0, 3):
                                        sum_means=means.iloc[j-start_day+k*days_total]['Cell_percent']
                                        # if j==0 and i==0:
                                        #     if 0.01<=tt_p[5-start_day,2]<0.05:
                                        #         text(j+0.05, m-0.05, '*' , fontsize=18)
                                        #     if 0.001<=tt_p[5-start_day,2]<0.01:
                                        #         text(j+0.05, m-0.05, '**' , fontsize=18)
                                        #     if tt_p[5-start_day,2]<0.001:
                                        #         text(j+0.05, m-0.05, '***' , fontsize=18)
                                        # else:
                                        m=m+sum_means
                                        if k==0:
                                            k_new=1
                                        if k==1:
                                            k_new=2
                                        if k==2:
                                            k_new=0
                                        if 0.01<=tt_p[j-start_day,k_new]<0.05:
                                            text(j-start_day+0.05, m-0.05, '*' , fontsize=18)
                                        if 0.001<=tt_p[j-start_day,k_new]<0.01:
                                            text(j-start_day+0.05, m-0.05, '**' , fontsize=18)
                                        if tt_p[j-start_day,k_new]<0.001:
                                            text(j-start_day+0.05, m-0.05, '***' , fontsize=18)

                        #endregion

                        #region lineplots
                        if plot_type=="line":

                            mi_new = mi[mi['Condition'] == i]
                            mi_new = mi_new[mi_new['Marker'] == 'RFP']

                            mi_new['norm'] = 0.

                            mi_new=mi_new.reset_index(drop=True)

                            m_base = mi_new[mi_new['Day'] == start_day]
                            m_base = m_base.reset_index(drop=True)

                            for day in range(mi['Day'].min(),mi['Day'].max()+1):
                                m_day = mi_new[mi_new['Day'] == day]
                                ind = m_day.index
                                m_day = m_day.reset_index(drop=True)

                                if normalization_type == 'relative':
                                    m_day['norm'] = (m_day[stats_var] - m_base[stats_var]) / m_base[stats_var]
                                else:
                                    m_day['norm'] = (m_day[stats_var]) / m_base[stats_var]
                                k=0
                                for j in ind:
                                    mi_new['norm'].iloc[j] = m_day['norm'].iat[k]
                                    k=k+1

                            means = mi_new.groupby(['Day']).mean()
                            stds = mi_new.groupby(['Day']).std()

                            if i==control_condition:
                                mi_new_control=mi_new
                                ax = sns.lineplot(x='Day', y='norm', data=mi_new_control,ci='sd')  # ,palette = sns.color_palette("hsv", 2))#, err_style = "bars")

                            else:
                                mi_new_both=mi_new.append(mi_new_control)
                                hue_choice = [control_condition, i]
                                ax = sns.lineplot(x='Day', y='norm', data=mi_new_both, hue=hue_split,hue_order=hue_choice,legend='full',
                                                  ci='sd', palette = sns.color_palette("hsv", 2), style=hue_split, markers=True, dashes=True)#, err_style = "bars")

                            handles, labels = ax.get_legend_handles_labels()
                            ax.legend(handles, labels, loc='upper left')

                            x_days = np.arange(start_day, end_day+1)
                            # print(x_days)
                            plt.xticks(x_days)
                            # ax.set_xticklabels(x_days, rotation=0)
                            # ax.set_xticklabels([0,0,1,2,3,4,5,6,7,8,9,10], rotation=0)
                            ax.set_ylabel('Normalized Cell Count')
                            ax.set_title(ax_title)

                            if do_ttest:
                                for j in range(mi['Day'].min(),mi['Day'].max()+1):
                                    m=means.iloc[j-start_day]['norm']
                                    if 0.01<=tt_p[j-start_day]<0.05:
                                        text(j, m+0.05, '*' , fontsize=18 , horizontalalignment='center')
                                    if 0.001<=tt_p[j-start_day]<0.01:
                                        text(j, m+0.05, '**' , fontsize=18 , horizontalalignment='center')
                                    if tt_p[j-start_day]<0.001:
                                        text(j, m+0.05, '***' , fontsize=18 , horizontalalignment='center')


                        #endregion

                        #region Global plot parameters
                        ax.grid(False)

                        if x_var=="Condition":
                            ax.set_xticklabels(ax.get_xticklabels(),rotation=30)

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


                l=l+1

                #endregion

            #region save stats
            if save_excel_stats:
                if do_ttest:
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


                if do_anova:

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
                                # print(arr_shape)
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
                                # print(arr_shape)
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
                            # print(aov_table_all)
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

                if stats_var=='Total':
                    mi_box=mi
                    mi_box = mi_box[mi_box.Marker == marker_list[0]]


                    mi_box=mi_box.loc[mi_box['Condition'].isin(conditions)]
                    sorterIndex = dict(zip(conditions, range(len(conditions))))

                    # Generate a rank column that will be used to sort
                    # the dataframe numerically
                    mi_box['Condition_Rank'] = mi_box['Condition'].map(sorterIndex)
                    mi_box.sort_values(['Condition_Rank','WellNum'], ascending = [True,True], inplace = True)
                    mi_box.drop('Condition_Rank', 1, inplace=True)

                    mi_box['norm'] = 0.

                    mi_box = mi_box.reset_index(drop=True)

                    mi_base = mi_box[mi_box['Day'] == start_day]
                    mi_base = mi_base.reset_index(drop=True)


                    m_day = mi_box[mi_box['Day'] == box_day]
                    ind = m_day.index
                    m_day = m_day.reset_index(drop=True)

                    if normalization_type == 'relative':
                        m_day['norm'] = (m_day[stats_var] - mi_base[stats_var]) / mi_base[stats_var]
                    else:
                        m_day['norm'] = (m_day[stats_var]) / mi_base[stats_var]

                    k = 0
                    for j in ind:
                        mi_box['norm'].iloc[j] = m_day['norm'].iat[k]
                        k = k + 1

                    mi_box= mi_box[mi_box.Day == box_day]

                    ax = sns.boxplot(x="Condition", y='norm', data=mi_box, linewidth=2, fliersize=0)
                    ax = sns.swarmplot(x="Condition", y='norm', data=mi_box, size=15, color='#767676',edgecolor="white",linewidth=1)

                    custom_lines = [Line2D([0], [0], color="#5fa2ce", lw=4),
                                    Line2D([0], [0], color="#ffbc79", lw=4),
                                    Line2D([0], [0], color="#fc7d0b", lw=4),
                                    Line2D([0], [0], color="#c85200", lw=4),
                                    Line2D([0], [0], color="#1170aa", lw=4)]
                    ax.legend(custom_lines,
                              ['-Control', '+Control', 'Novel Combo', 'Novel Repurposed', 'Published \nor In Use'],
                              loc='upper left', bbox_to_anchor=(0.14, 0.98))

                    for iii in range(1,len(conditions)):
                        con_group1=control_condition
                        con_group2=conditions[iii]

                        df_05_con=df_05[df_05['group1']==con_group1]
                        df_05_con=df_05_con[df_05_con['group2']==con_group2]
                        df_05_con=df_05_con[df_05_con['Day']==box_day]
                        df_05_con=df_05_con.reset_index(drop=True)
                        reject_05=df_05_con.iloc[0]['reject']

                        df_01_con=df_01[df_01['group1']==con_group1]
                        df_01_con=df_01_con[df_01_con['group2']==con_group2]
                        df_01_con=df_01_con[df_01_con['Day']==box_day]
                        df_01_con=df_01_con.reset_index(drop=True)
                        reject_01=df_01_con.iloc[0]['reject']

                        df_001_con=df_001[df_001['group1']==con_group1]
                        df_001_con=df_001_con[df_001_con['group2']==con_group2]
                        df_001_con=df_001_con[df_001_con['Day']==box_day]
                        df_001_con=df_001_con.reset_index(drop=True)
                        reject_001=df_001_con.iloc[0]['reject']

                        ymin, ymax = ax.get_ylim()
                        lines = ax.get_lines()
                        categories = ax.get_xticks()
                        # every 4th line at the interval of 6 is median line
                        # 0 -> p25 1 -> p75 2 -> lower whisker 3 -> upper whisker 4 -> p50 5 -> upper extreme value

                        y = round(lines[3 + iii * 6].get_ydata()[0], 1)

                        if reject_001:
                            text(iii -0.15, y + 0.7, '***', fontsize=40,color='black')
                        elif reject_01:
                            text(iii -0.1, y + 0.7, '**', fontsize=40,color='black')
                        elif reject_05:
                            text(iii -0.05, y + 0.7, '*', fontsize=40,color='black')

                    ax.grid(True)
                    # ax.set(ylim=(0, 1.2))
                    fig = plt.gcf()
                    fig.set_size_inches(30, 15)
                    plt.gcf().subplots_adjust(bottom=0.3)

                    # ax.set_xticklabels(conditions, rotation=90)
                    # ax.set(xticks=ttest_pvalues.columns, rotation=90)
                    tick_list = np.r_[0:len(conditions)]
                    ax.set_xticks(tick_list)
                    # print(conditions)
                    ax.set_xticklabels(conditions, rotation=37, ha='right')  # , rotation_mode="anchor")
                    # for tick in ax.xaxis.get_majorticklabels():
                    #     tick.set_horizontalalignment("right")
                    ax.set_ylabel('Normalized Cell Counts')
                    # ax.set_xlabel('Conditions')
                    ax.set_xlabel('')

                    ax.set_title(ax_title_boxplot)

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

                    means = mi_new2.groupby(['Condition', 'Marker'], sort=False).mean()
                    stds = mi_new2.groupby(['Condition', 'Marker'], sort=False).std()

                    ax = means.Cell_percent.unstack().plot(kind='bar', yerr=stds.Cell_percent.unstack(),
                                                           stacked=True,
                                                           capsize=5, color=['yellow', 'orange', 'red'],
                                                           sort_columns=True)

                    handles, labels = ax.get_legend_handles_labels()
                    # box = ax.get_position()
                    # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                    ax.legend(reversed(handles), reversed(labels), loc='upper right', bbox_to_anchor=(1.2, 0.8))

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
                    ax.set_xticklabels(conditions, rotation=37, ha='right')  # , rotation_mode="anchor")
                    for tick in ax.xaxis.get_majorticklabels():
                        tick.set_horizontalalignment("right")


                    ax.set_title(ax_title_stackedbar)

                    if do_ttest:
                        j=box_day
                        m = 0
                        for con_bar in range(0,len(conditions)):
                            for k in range(0, 3):
                                # print(means)
                                # print(3*con_bar+k)
                                sum_means = means.iloc[3*con_bar+k]['Cell_percent']
                                # sum_means = means.iloc[j - start_day + k * days_total]['Cell_percent']
                                m = m + sum_means
                                if k == 0:
                                    k_new = 1
                                if k == 1:
                                    k_new = 2
                                if k == 2:
                                    k_new = 0

                                # tt_all = np.zeros((3, len(days), len(conditions), 3))
                                # print(tt_all[0, j - start_day, con_bar,k_new])
                                # print('k:',k_new,'m:',m)
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

                if stats_var == 'Total':
                    mi_box = mi
                    mi_box = mi_box[mi_box.Marker == marker_list[0]]

                    # for con in conditions:
                    #     mi_box = mi_box[mi_box.Condition != con]

                    mi_box = mi_box.loc[mi_box['Condition'].isin(conditions)]
                    sorterIndex = dict(zip(conditions, range(len(conditions))))

                    # Generate a rank column that will be used to sort
                    # the dataframe numerically
                    mi_box['Condition_Rank'] = mi_box['Condition'].map(sorterIndex)
                    mi_box.sort_values(['Condition_Rank', 'WellNum'], ascending=[True, True], inplace=True)
                    mi_box.drop('Condition_Rank', 1, inplace=True)
                    # print(mi_box['Condition'])

                    mi_box['norm'] = 0.

                    mi_box = mi_box.reset_index(drop=True)

                    mi_base = mi_box[mi_box['Day'] == start_day]
                    mi_base = mi_base.reset_index(drop=True)

                    for day in range(mi['Day'].min(), mi['Day'].max() + 1):
                        m_day = mi_box[mi_box['Day'] == day]
                        ind = m_day.index
                        m_day = m_day.reset_index(drop=True)

                        if normalization_type == 'relative':
                            m_day['norm'] = (m_day[stats_var] - mi_base[stats_var]) / mi_base[stats_var]
                        else:
                            m_day['norm'] = (m_day[stats_var]) / mi_base[stats_var]
                        k = 0
                        for j in ind:
                            mi_box['norm'].iloc[j] = m_day['norm'].iat[k]
                            k = k + 1


                    # ax = sns.lineplot(x='Day', y='norm', data=mi_box,
                    #                       ci='sd')  # ,palette = sns.color_palette("hsv", 2))#, err_style = "bars")


                    ax = sns.lineplot(x='Day', y='norm', data=mi_box, hue='Condition', linewidth=6,
            
                                      legend='full', ci=None)#,  err_style = "bars")#,err_kws=capsize)
                                      # legend='full', ci='sd')#,  err_style = "bars")#,err_kws=capsize)
                    # style = hue_split, markers = True, dashes = True,
                    # , palette = sns.color_palette("hsv", 2)
                    handles, labels = ax.get_legend_handles_labels()
                    for legobj in handles:
                        legobj.set_linewidth(6.0)
                    vertical_line_label = 'Removal of Drug'
                    x0 = 6
                    plt.axvline(x0, color='black', linestyle='--', linewidth=3, label=vertical_line_label)

                    ax.grid(True)

                    x_days = np.arange(start_day, end_day + 1)
                    plt.xticks(x_days)

                    # ax.set(ylim=(0, 1.2))
                    fig = plt.gcf()
                    fig.set_size_inches(20, 20)
                    # fig = plt.figure(figsize=(30, 30), dpi=300)
                    box = ax.get_position()

                    plt.gcf().subplots_adjust(bottom=0.3)

                    # ax.set_xticklabels(conditions, rotation=90)
                    # ax.set(xticks=ttest_pvalues.columns, rotation=90)
                    # tick_list = np.r_[0:len(conditions)]
                    # ax.set_xticks(tick_list)
                    # print(conditions)
                    # ax.set_xticklabels(conditions, rotation=37, ha='right')  # , rotation_mode="anchor")
                    # for tick in ax.xaxis.get_majorticklabels():
                    #     tick.set_horizontalalignment("right")
                    ax.set_ylabel('Normalized Cell Counts')
                    # ax.set_xlabel('Conditions')
                    # ax.set_xlabel('')

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

    print("Total time passed in s: %s" % round((time.time() - start_time), 2))

if __name__ == "__main__":
    # Use commandline argument for directory if provided, otherwise default to current directory
    try:
        base_directory = sys.argv[1]
    except IndexError:
        base_directory = os.getcwd()

    filepaths = [os.path.join(base_directory, 'data', f'frame_m{frame}_processed_data.csv') for frame in [1, 2]]

    # TODO: SWITCH BACK TO THIS
    # stats_vars = ['Cell_percent','Total']   # ['Cell_percent'] (use stacked barplots) or ['Total'] (use lineplots), or  ['Cell_percent','Total'] for both
    stats_vars = ['Total']
    x_var = "Day"  # x_axis variable, mostly 'Day' right now for all major plots (line, stacked bar and colormap)

    normalization_type = 'total' # 'relative' or 'total'

    do_ttest = False  # currently set for all conditions. needed for plotting line and stacked bar plots with stars, as well as for colormaps
    do_wilcoxon_test = False # needs do_ttest to be set to True, as it works from within it and just replaces the actual test function
    do_anova = False
    do_tukey_test = False

    save_excel_stats = True  # True = saves stats to csv or xls files. needed for colormap-plots

    plots = True  # True = create plots
    colormap_plot = False  # create color map of stat results
    cmap_discrete = False  # True = discrete, False = continous
    individual_plots = True # create individual line and/or bar graph plots

    boxplots = False # True for DO IT (only for total)
    stackedbarplots = False # only for Cell percent
    lineplots = True # still working on this
    box_day = 5

    save_plots = True  # True = save all plots,  or False = stops at each condition to show plot without saving it

    plot_context = 'talk'  # 'talk', 'poster', 'notebook' - use talk for now

    hue_split = "Condition"  # "Percent" or 'Condition'. mostly 'Condition' right now for all major plots (line, stacked bar and colormap)

    create_plots_and_stats(
        stats_vars=stats_vars,
        x_var=x_var,
        filepaths=filepaths,
        normalization_type=normalization_type,
        do_ttest=do_ttest,
        do_wilcoxon_test=do_wilcoxon_test,
        do_anova=do_anova,
        do_tukey_test=do_tukey_test,
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
        hue_split=hue_split
    )
