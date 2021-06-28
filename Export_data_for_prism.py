import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\Fucci_analysis\\NG108_FUCCI_Used\\all_data_together"

colnames=['Total','Total_total_normalized_norm', 'Total_relative_normalized_norm', 'Total_total_normalized_norm_log2', 'Total_relative_normalized_norm_log2', 'Total_total_fold_change_norm_Control_DMSO', 'Total_relative_fold_change_norm_Control_DMSO','Total_total_fold_change_norm_log2_Control_DMSO','Total_relative_fold_change_norm_log2_Control_DMSO']

root = tk.Tk()
root.withdraw()

# m1_filepath,m2_filepath = filedialog.askopenfilename(initialdir=Custom_dir,
m_all_filepath = filedialog.askopenfilename(initialdir=BASE_DIR,
                title="Select data file to convert to prism format",
                filetypes=(("csv", "*.csv"),))

mi_all=pd.read_csv(m_all_filepath)

Days_list = mi_all['Day'].to_numpy()
days=np.unique(Days_list)

Con_list = mi_all['Condition'].to_numpy()
con_list=np.unique(Con_list)

mi_all = mi_all[mi_all.Marker == 'RFP']

mi_all['Total_total_normalized_norm_log2'] = mi_all['Total_total_normalized_norm_log2'].astype(float)
mi_all['Total_relative_normalized_norm_log2'] = mi_all['Total_relative_normalized_norm_log2'].astype(float)
mi_all['Total_total_fold_change_norm_log2_Control_DMSO'] = mi_all['Total_total_fold_change_norm_log2_Control_DMSO'].astype(
    float)
mi_all['Total_relative_fold_change_norm_log2_Control_DMSO'] = mi_all[
    'Total_relative_fold_change_norm_log2_Control_DMSO'].astype(float)

mi_all = mi_all.groupby(['Day', 'Condition', 'Date'], sort=False, as_index=False).mean()

for norm_colname in colnames:

    for day in days:
        mi_day = mi_all[mi_all.Day == day]

        for con in con_list:
            mi_con = mi_day[mi_day.Condition == con]

            mi_conditions_bio_repeats=mi_con[norm_colname].to_frame().reset_index(drop=True)
            mi_conditions_bio_repeats=mi_conditions_bio_repeats.rename(columns={norm_colname: con})

            if con == con_list[0]:
                mi_conditions_bio_repeats_all = mi_conditions_bio_repeats.copy()
            else:
                mi_conditions_bio_repeats_all[con] = mi_conditions_bio_repeats


        m_all_filepath_save=m_all_filepath.replace('frame_mean','Prism_day_'+str(day)+'_mean')
        m_all_filepath_save=m_all_filepath_save.replace('processed_data',norm_colname)
        prism_days_vs_condition_Total = mi_conditions_bio_repeats_all.to_csv(
            m_all_filepath_save, index=None,
            header=True)  # Don't forget to add '.csv' at the end of the path
