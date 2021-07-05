import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\Fucci_analysis\\NG108_FUCCI_Used\\all_data_together"

list1=['Retigabine_10uM_Chlorozoxizone_100uM','Pantoprazole_100uM_Chlorozoxizone_100uM','Pantoprazole_50uM_Chlorozoxizone_100uM','Pantoprazole_100uM_Lamotrigine_100uM',
       'Pantoprazole_50uM_Lamotrigine_100uM','Pantoprazole_50uM']
list2=['Pantoprazole_100uM','NS1643_20uM','Pantoprazole_100uM_NS1643_20uM','Pantoprazole_100uM_Rapamycin_100nM','Rapamycin_100nM','NS1643_50uM_Chlorozoxizone_100uM']
list3=['Retigabine_10uM','Pantoprazole_100uM_Retigabine_10uM','NS1643_50uM','Pantoprazole_100uM_NS1643_50uM','TMZ_50uM','Pantoprazole_100uM_TMZ_50uM']
list4=['NS1643_50uM_TMZ_50uM','Control_DMSO','Pantoprazole_50uM_TMZ_50uM','NS1643_20uM_TMZ_50uM','Control_DMSO_3','Control']

lists=[list1, list2, list3, list4]

root = tk.Tk()
root.withdraw()

# m1_filepath,m2_filepath = filedialog.askopenfilename(initialdir=Custom_dir,
filepaths = filedialog.askopenfilename(initialdir=BASE_DIR,
                title="Select data file to get fucci differences",
                multiple=True,
                filetypes=(("csv", "*.csv"),))

for i in range(0,len(filepaths)):
    mi_filepath=filepaths[i]
    list=lists[i]

    mi=pd.read_csv(mi_filepath, header=None, names=['PlateNum','WellNum','Marker','Count','Count_Diff'])

    mi_rfp=mi.loc[mi.Marker==0]
    mi_rfp.reset_index(drop=False,inplace=True)
    mi_yfp=mi.loc[mi.Marker==1]
    mi_yfp.reset_index(drop=False,inplace=True)

    mi_mixed=pd.concat([mi_rfp['PlateNum'],mi_rfp['WellNum'],mi_rfp['Count'],mi_yfp['Count_Diff']],axis=1)
    mi_mixed.rename(columns={'Count':'Dead','Count_Diff':'Alive'},inplace=True)

    mi_mixed=pd.concat([mi_mixed,mi_yfp['Count']],axis=1)
    mi_mixed.rename(columns={'Count':'Total',},inplace=True)

    mi_mixed['Percent_Dead']=mi_mixed['Dead']/mi_mixed['Total']
    mi_mixed['Percent_Alive']=mi_mixed['Alive']/mi_mixed['Total']

    mi_mixed['Condition'] = ''

    for ii in range(0,len(list)):
        mi_mixed.iloc[0+10*ii:10+10*ii]['Condition'] = list[ii]

    mi_filepath_save = mi_filepath.replace('_M1', '_M1_Processed')

    mi_mixed.to_csv(mi_filepath_save)

    if i==0:
        mi_all=mi_mixed.copy()
    else:
        mi_all=mi_all.append(mi_mixed)

mi_filepath_save = mi_filepath_save.replace('Plate_4_M1_Processed', 'M1_Processed_All')
mi_all.reset_index(inplace=True)
mi_all.to_csv(mi_filepath_save)
