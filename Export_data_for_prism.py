import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import os
import glob as glob

# region pick repeats
repeats=['biological']
# repeats=['biological']  # enter ['biological','technical'] or delete one of them
# end region

period=2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\Fucci_analysis\\NG108_FUCCI_Used\\all_data_together"

# colnames=['Total','Total_total_normalized_norm', 'Total_relative_normalized_norm', 'Total_total_normalized_norm_log2',
#           'Total_relative_normalized_norm_log2', 'Total_total_fold_change_norm_Control_DMSO',
#           'Total_relative_fold_change_norm_Control_DMSO','Total_total_fold_change_norm_log2_Control_DMSO',
#           'Total_relative_fold_change_norm_log2_Control_DMSO', 'Slope_total_normalized_norm_log2',
#           'Slope_total_fold_change_norm_log2_Control_DMSO', 'Slope_Diff_total_fold_change_norm_log2_Control_DMSO',
#           'Slope_Diff_total_normalized_norm_log2']
# colnames=['Total','Total_total_normalized_norm', 'Total_total_normalized_norm_log2', 'Total_total_fold_change_norm_Control_DMSO','Total_total_fold_change_norm_log2_Control_DMSO']

colnames=['Total','Total_total_normalized_norm', 'Total_total_normalized_norm_log2', 'Slope_total_normalized_norm_log2',
          'Slope_total_normalized_norm']#,'Slope_Diff_total_normalized_norm_log2']

root = tk.Tk()
root.withdraw()

# m1_filepath,m2_filepath = filedialog.askopenfilename(initialdir=Custom_dir,
m_all_filepath = filedialog.askopenfilename(initialdir=BASE_DIR,
                title="Select data file to convert to prism format",
                filetypes=(("csv", "*.csv"),))

Custom_dir=os.path.dirname(m_all_filepath)

def export_prism_data(m_all_filepath,repeat):
    mi_all = pd.read_csv(m_all_filepath)

    drug_list_fpath = glob.glob(Custom_dir + '/*Drug_List.csv')
    if len(drug_list_fpath) > 0:
        drug_list_df = pd.read_csv(drug_list_fpath[0])
        drug_list = drug_list_df['Condition'].to_list()
    else:
        drug_list = []

    mi_all = mi_all.loc[mi_all['Condition'].isin(drug_list)]

    mi_all = mi_all[mi_all.Day % 2 == 0]
    mi_all.reset_index(inplace=True)
    Days_list = mi_all['Day'].to_numpy()
    days=np.unique(Days_list)

    Con_list = mi_all['Condition'].to_numpy()
    con_list=np.unique(Con_list)
    con_list = con_list.tolist()

    mi_all = mi_all[mi_all.Marker == 'RFP']

    mi_all['Total'] = mi_all['Total'].astype(float)
    mi_all['Total_total_normalized_norm_log2'] = mi_all['Total_total_normalized_norm_log2'].astype(float)
    # mi_all['Total_relative_normalized_norm_log2'] = mi_all['Total_relative_normalized_norm_log2'].astype(float)
    mi_all['Total_total_normalized_norm'] = mi_all['Total_total_normalized_norm'].astype(float)
    # mi_all['Total_total_fold_change_norm_log2_Control_DMSO'] = mi_all['Total_total_fold_change_norm_log2_Control_DMSO'].astype(
    #     float)
    # mi_all['Total_relative_fold_change_norm_log2_Control_DMSO'] = mi_all[
    #     'Total_relative_fold_change_norm_log2_Control_DMSO'].astype(float)

    # slopes=mi_all.groupby(['Day', 'Condition', 'Date', 'PlateNum', 'WellNum'], sort=False, as_index=False)
    mi_all['Slope_total_normalized_norm_log2']=mi_all.Total_total_normalized_norm_log2.diff(periods=period)/(2*period)
    mi_all['Slope_total_normalized_norm']=mi_all.Total_total_normalized_norm.diff(periods=period)/(2*period)
    # mi_all['Slope_total_fold_change_norm_log2_Control_DMSO']=mi_all.Total_total_fold_change_norm_log2_Control_DMSO.diff(periods=2)/2

    # mi_all['Slope_Diff_total_normalized_norm_log2'] = mi_all.Slope_total_normalized_norm_log2.diff(periods=period)
    # mi_all['Slope_Diff_total_normalized_norm'] = mi_all.Slope_total_normalized_norm.diff(periods=period)
    # mi_all['Slope_Diff_total_fold_change_norm_log2_Control_DMSO'] = mi_all.Slope_total_fold_change_norm_log2_Control_DMSO.diff(periods=2)

    if repeat=='biological':
        mi_all = mi_all.groupby(['Day', 'Condition', 'Date'], sort=False, as_index=False).mean()
        date_list='all'
    if repeat == 'technical':
        mi_all = mi_all.groupby(['Day', 'Condition', 'Date', 'PlateNum', 'WellNum'], sort=False, as_index=False).mean()
        Date_list = mi_all['Date'].to_numpy()
        date_list = np.unique(Date_list)



    for date in date_list:

        if repeat=='technical':
            mi_date=mi_all[mi_all.Date == date]
        else:
            mi_date=mi_all

        for norm_colname in colnames:

            for day in days:
                mi_day = mi_date[mi_date.Day == day]

                control_condition='Control_DMSO'
                con_list.remove(control_condition)
                con_list.insert(0, control_condition)
                for con in con_list:
                    mi_con = mi_day.loc[mi_day.Condition == con]

                    mi_conditions_bio_repeats=mi_con[norm_colname].to_frame().reset_index(drop=True)
                    # print(mi_conditions_bio_repeats)
                    mi_conditions_bio_repeats=mi_conditions_bio_repeats.rename(columns={norm_colname: con})

                    if con == con_list[0]:
                        mi_conditions_bio_repeats_all = mi_conditions_bio_repeats.copy()
                        # print(mi_conditions_bio_repeats_all)
                    else:

                        # print(con)
                        # print(mi_conditions_bio_repeats)
                        mi_conditions_bio_repeats_all[con] = mi_conditions_bio_repeats

                dir_pos = m_all_filepath.rfind('/')
                dir = m_all_filepath[:dir_pos]
                save_dir=dir + '/' + repeat + '_prism_data_format/'

                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)

                m_all_filepath_save=save_dir+m_all_filepath[dir_pos:]

                if repeat=='technical':
                    m_all_filepath_save = m_all_filepath_save.replace('frame_mean','Prism_'+ date+ '_day_'+str(day)+'_mean')
                else:
                    m_all_filepath_save=m_all_filepath_save.replace('frame_mean','Prism_day_'+str(day)+'_mean')
                m_all_filepath_save=m_all_filepath_save.replace('processed_data',norm_colname)

                mi_conditions_bio_repeats_all.dropna(how='all', axis=1, inplace=True)

                mi_conditions_bio_repeats_all.to_csv(m_all_filepath_save, index=None,
                    header=True)  # Don't forget to add '.csv' at the end of the path

# biological repeats:

for repeat in repeats:
    print('processing ', repeat, ' repeats....')
    export_prism_data(m_all_filepath,repeat)