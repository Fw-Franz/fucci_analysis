import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="D:\hisc_data"

colnames=['Dead', 'Alive', 'Total', 'Percent_Dead', 'Percent_Alive']

root = tk.Tk()
root.withdraw()

m_all_filepath = filedialog.askopenfilename(initialdir=Custom_dir,
# m_all_filepath = filedialog.askopenfilename(initialdir=BASE_DIR,
                title="Select data file to convert to prism format",
                filetypes=(("csv", "*.csv"),))

def export_prism_data(m_all_filepath):
    mi_all = pd.read_csv(m_all_filepath)


    Con_list = mi_all['Condition'].to_numpy()
    con_list=np.unique(Con_list)
    con_list = con_list.tolist()

    mi_all = mi_all.groupby([ 'Condition', 'PlateNum', 'WellNum'], sort=False, as_index=False).mean()

    for norm_colname in colnames:

        control_condition='Control_DMSO'
        con_list.remove(control_condition)
        con_list.insert(0, control_condition)
        for con in con_list:
            mi_con = mi_all.loc[mi_all.Condition == con]

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
        save_dir=dir + '/_prism_data_format/'

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        m_all_filepath_save=save_dir+m_all_filepath[dir_pos:]

        m_all_filepath_save=m_all_filepath_save.replace('FucciResults','Prism_data')

        m_all_filepath_save=m_all_filepath_save.replace('Processed',norm_colname)

        mi_conditions_bio_repeats_all.dropna(how='all', axis=1, inplace=True)

        mi_conditions_bio_repeats_all.to_csv(m_all_filepath_save, index=None,
            header=True)  # Don't forget to add '.csv' at the end of the path

export_prism_data(m_all_filepath)