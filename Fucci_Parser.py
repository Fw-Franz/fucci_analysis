import numpy as np
import pandas as pd
import time
import os
import tkinter as tk
from tkinter import filedialog

###############
# Does your file includes different time points (Days)? if so, set days to True. if not, set to False
days=False
######################


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\Fucci_analysis\\NG108_FUCCI_Used\\all_data_together"

root = tk.Tk()
root.withdraw()

#region Input parameters
# input_dir_base = filedialog.askdirectory(initialdir=Custom_dir,
input_dir_base = filedialog.askdirectory(initialdir=BASE_DIR,
                title="Select Antibody Results Directory")
dir_list = os.listdir(input_dir_base)
# endregion

start_time = time.time()

for input_dir in dir_list:

    print('processing ', input_dir)
    print('--------------------')

    sub_dir= input_dir_base + '/' + input_dir + '/'# you can just write this as << save_dir = input_dir_base  >> if you want to save it in the same base directory as the input files, otherweise specify other directory

    # input_fname_rfp="MyExpt_RFP_obj.csv"
    # input_fname_yfp="MyExpt_YFP_obj.csv"

    input_fname_rfp="MyExpt_RFP_Nuclei.csv"
    input_fname_yfp="MyExpt_YFP_Nuclei.csv"

    input_fname_rfp_yfp="MyExpt_RFP_YFP.csv"

    df_rfp=pd.read_csv(sub_dir+input_fname_rfp)
    df_yfp=pd.read_csv(sub_dir+input_fname_yfp)
    df_rfp_yfp=pd.read_csv(sub_dir+input_fname_rfp_yfp)

    if days:
        mi_rfp=df_rfp[['ImageNumber','Metadata_Plate','Metadata_Timepoint','Metadata_Day']]
        mi_rfp = mi_rfp.rename(columns={"Metadata_Plate": "PlateNum","Metadata_Timepoint": "WellNum","Metadata_Day": "DayNum"})
    else:
        mi_rfp=df_rfp[['ImageNumber','Metadata_Plate','Metadata_Timepoint']]
        mi_rfp = mi_rfp.rename(columns={"Metadata_Plate": "PlateNum","Metadata_Timepoint": "WellNum"})

    mi_rfp['Marker']=0
    mi_rfp['Count'] = mi_rfp.groupby(by='ImageNumber')['ImageNumber'].transform('count')
    mi_rfp = mi_rfp.drop_duplicates()

    if days:
        mi_yfp=df_yfp[['ImageNumber','Metadata_Plate','Metadata_Timepoint','Metadata_Day']]
        mi_yfp = mi_yfp.rename(columns={"Metadata_Plate": "PlateNum","Metadata_Timepoint": "WellNum","Metadata_Day": "DayNum"})
    else:
        mi_yfp=df_yfp[['ImageNumber','Metadata_Plate','Metadata_Timepoint']]
        mi_yfp = mi_yfp.rename(columns={"Metadata_Plate": "PlateNum","Metadata_Timepoint": "WellNum"})

    mi_yfp['Marker']=1
    mi_yfp['Count'] = mi_yfp.groupby(by='ImageNumber')['ImageNumber'].transform('count')
    mi_yfp = mi_yfp.drop_duplicates()

    if days:
        mi_rfp_yfp=df_rfp_yfp[['ImageNumber','Metadata_Plate','Metadata_Timepoint','Metadata_Day']]
        mi_rfp_yfp = mi_rfp_yfp.rename(columns={"Metadata_Plate": "PlateNum","Metadata_Timepoint": "WellNum","Metadata_Day": "DayNum"})
    else:
        mi_rfp_yfp=df_rfp_yfp[['ImageNumber','Metadata_Plate','Metadata_Timepoint']]
        mi_rfp_yfp = mi_rfp_yfp.rename(columns={"Metadata_Plate": "PlateNum","Metadata_Timepoint": "WellNum"})

    mi_rfp_yfp['Marker']=2
    mi_rfp_yfp['Count'] = mi_rfp_yfp.groupby(by='ImageNumber')['ImageNumber'].transform('count')
    mi_rfp_yfp = mi_rfp_yfp.drop_duplicates()

    mi=pd.concat([mi_rfp,mi_yfp,mi_rfp_yfp])

    mi.sort_values(['ImageNumber', 'Marker'],
                        ascending=[True, True], inplace=True)

    mi['yfp_rfp_diff']=mi.Count.diff()

    mi = mi.drop(columns=['ImageNumber'])

    mi.to_csv(path_or_buf=sub_dir + input_dir  + '_FucciResultsCounts.csv',  index=None, header=None)

    print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))