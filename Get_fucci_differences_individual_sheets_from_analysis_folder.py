import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import os
import glob

pd.set_option('mode.chained_assignment',None)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\Fucci_analysis\\NG108_FUCCI_Used\\all_data_together"

list=['Control_DMSO','Pantoprazole_100uM','NS1643_50uM','Pantoprazole_100uM_NS1643_50uM',
       'Retigabine_10uM','Pantoprazole_100uM_Retigabine_10uM']
# list=['Control_DMSO','TMZ_50uM','NS1643_50uM','Pantoprazole_100uM','Pantoprazole_100uM_TMZ_50uM','NS1643_50uM_TMZ_50uM']

days=False

base_directory=os.getcwd()+'//'
sub_dir= os.path.basename(os.getcwd())

filepath_rfp=glob.glob(base_directory + '*MyExpt_RFP_Nuclei.csv')
filepath_yfp=glob.glob(base_directory + '*MyExpt_YFP_Nuclei.csv')

df_rfp = pd.read_csv(filepath_rfp[0])
df_yfp = pd.read_csv(filepath_yfp[0])

if days:
    mi_rfp = df_rfp[['ImageNumber', 'Metadata_Plate', 'Metadata_Timepoint', 'Metadata_Day']]
    mi_rfp = mi_rfp.rename(
        columns={"Metadata_Plate": "PlateNum", "Metadata_Timepoint": "WellNum", "Metadata_Day": "DayNum"})
else:
    mi_rfp = df_rfp[['ImageNumber', 'Metadata_Plate', 'Metadata_Timepoint']]
    mi_rfp = mi_rfp.rename(columns={"Metadata_Plate": "PlateNum", "Metadata_Timepoint": "WellNum"})

mi_rfp['Marker'] = 0
mi_rfp['Count'] = mi_rfp.groupby(by='ImageNumber')['ImageNumber'].transform('count')
mi_rfp = mi_rfp.drop_duplicates()

if days:
    mi_yfp = df_yfp[['ImageNumber', 'Metadata_Plate', 'Metadata_Timepoint', 'Metadata_Day']]
    mi_yfp = mi_yfp.rename(
        columns={"Metadata_Plate": "PlateNum", "Metadata_Timepoint": "WellNum", "Metadata_Day": "DayNum"})
else:
    mi_yfp = df_yfp[['ImageNumber', 'Metadata_Plate', 'Metadata_Timepoint']]
    mi_yfp = mi_yfp.rename(columns={"Metadata_Plate": "PlateNum", "Metadata_Timepoint": "WellNum"})

mi_yfp['Marker'] = 1
mi_yfp['Count'] = mi_yfp.groupby(by='ImageNumber')['ImageNumber'].transform('count')
mi_yfp = mi_yfp.drop_duplicates()

mi = pd.concat([mi_rfp, mi_yfp])

mi.sort_values(['ImageNumber', 'Marker'],
               ascending=[True, True], inplace=True)

# df.set_index('PlateNum').reindex(range(df['PlateNum'].min(),df['PlateNum'].max())).fillna(0).reset_index()
mi['marker_diff']=mi.Marker.diff()
i=0

mi.reset_index(drop=False,inplace=True)
mod_df=mi.copy()
for well in mi.WellNum:
    if mi.loc[(mi.WellNum==well),['marker_diff']].values[0]==0:
        mod_df=mod_df.append(mi.loc[(mi.WellNum == well)], ignore_index=True)
        if mi.loc[(mi.WellNum == well), ['Marker']].values[0] == 1:
            mod_df.Marker.iloc[-1] = 0
            mod_df.Count.iloc[-1] = 0
        if mi.loc[ (mi.WellNum == well), ['Marker']].values[0] == 0:
            mod_df.Marker.iloc[-1] = 1
            mod_df.Count.iloc[-1] = 0

if mod_df.Marker.iloc[0]== 1:
    mod_df = mod_df.append(mod_df.iloc[0], ignore_index=True)
    mod_df.Marker.iloc[-1] = 0
    mod_df.Count.iloc[-1] = 0

mi = mod_df.copy()
mi.sort_values(['ImageNumber', 'Marker'],
               ascending=[True, True], inplace=True)
mi['Count_Diff'] = mi.Count.diff()

mi = mi.drop(columns=['ImageNumber'])
mi = mi.drop(columns=['index'])
mi = mi.drop(columns=['marker_diff'])

mi.to_csv(path_or_buf=base_directory + sub_dir +'_FucciResultsCounts.csv', index=None, header=None)

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
    mi_mixed.iloc[0+5*ii:5+5*ii]['Condition'] = list[ii]

mi_mixed.to_csv(base_directory + sub_dir+ '_FucciResultsCounts_Processed.csv')
#
# if i==0:
#     mi_all=mi_mixed.copy()
# else:
#     mi_all=mi_all.append(mi_mixed)
#
# mi_filepath_save = mi_filepath_save.replace('Plate_4_M1_Processed', 'M1_Processed_All')
# mi_all.reset_index(inplace=True)
# mi_all.to_csv(mi_filepath_save)
