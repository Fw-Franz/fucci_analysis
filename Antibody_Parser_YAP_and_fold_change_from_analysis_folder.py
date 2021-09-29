import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import os
import numpy as np

# pd.set_option('mode.chained_assignment', 'raise')
pd.set_option('mode.chained_assignment', None)

#region Input parameters
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Custom_dir="Y:\\Juanita\\NewMethodAnalysisSheets\\1_13_21Allsheets\\RegAntibodies\\CMYC_cx43_cx46_GFAP_HDAC9_MAP2\\08_07_2021"
Current_dir=os.getcwd()

input_folder_name=os.path.basename(Current_dir)

row_B_drug_name='Control'
row_C_drug_name='Pantoprazole_100uM'
row_D_drug_name='NS1643_50uM'
row_E_drug_name='Pantoprazole_100uM_NS1643_50uM'
row_F_drug_name='Retigabine_10uM'
row_G_drug_name='Pantoprazole_100uM_Retigabine_10uM'

#endregion

start_time = time.time()

sub_dir= Current_dir

# input_fname_nuclei="/FilteredNuclei_from_EditedObjects.csv" # needs "/" in front
# input_fname_nuclei="/FilteredNuclei_from_Cytoplasm_by_Cytoplasm_normalized.csv" # needs "/" in front
input_fname_nuclei="/Cytoplasm_by_FilteredNuclei_normalized.csv" # needs "/" in front
# input_fname_nuclei="/Cytoplasm.csv" # needs "/" in front

df_nuclei=pd.read_csv(sub_dir+input_fname_nuclei)

mi=df_nuclei[['ImageNumber','ObjectNumber','FileName_DisplayImage','Intensity_MeanIntensity_OrigGreen','Intensity_IntegratedIntensity_OrigGreen']]
mi=mi.rename(columns={"Intensity_MeanIntensity_OrigGreen": "FarRed_mean_I",
                      "Intensity_IntegratedIntensity_OrigGreen": "FarRed_int_I"})

mi['Cell_Num']=mi.groupby(by='ImageNumber')['ImageNumber'].transform('count')

name = mi['FileName_DisplayImage'].values[0]

base_postion = name.find("_R_", 0, len(name))
row = name[base_postion + 9]
col = name[base_postion + 10:base_postion + 12]
frame = name[base_postion + 12:base_postion + 15]

print('row, col, frame: ', row, col, frame, '\n')

mi['Row']=mi.FileName_DisplayImage.str.slice(base_postion + 9, base_postion + 10)
mi['Column']=mi.FileName_DisplayImage.str.slice(base_postion + 10, base_postion + 12)
mi['Frame']=mi.FileName_DisplayImage.str.slice(base_postion + 12, base_postion + 15)

mi=mi.drop(columns=['FileName_DisplayImage'])

mi['Drug_Name']=mi['Row'].copy()
mi['Drug_Name'].loc[mi.Drug_Name=='B']=row_B_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='C']=row_C_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='D']=row_D_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='E']=row_E_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='F']=row_F_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='G']=row_G_drug_name

mi['Cell_Num'] = mi['Cell_Num'].astype(float)

mi.replace([np.inf, -np.inf], np.nan, inplace=True)

# Dropping all the rows with nan values
mi.dropna(inplace=True)


means_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).mean()
stds_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).std()

means_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).mean()
stds_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).std()

means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()

means_rows_control=means_rows.loc[means_rows.Drug_Name=='Control']

means_columns['Fold_change_FarRed_mean_I']=means_columns['FarRed_mean_I'].copy()/float(means_rows_control['FarRed_mean_I'])
means_columns['Fold_change_FarRed_int_I']=means_columns['FarRed_int_I'].copy()/float(means_rows_control['FarRed_int_I'])

means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()

mi.to_csv(path_or_buf=sub_dir + '\\' +input_folder_name +  '_AntibodyResults.csv',  index=None, header=True)

means_frame.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Frame_means.csv',  index=None, header=True)
means_columns.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Column_means.csv',  index=None, header=True)
means_rows.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Row_means.csv',  index=None, header=True)

stds_frame.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Frame_stds.csv',  index=None, header=True)
stds_columns.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Column_stds.csv',  index=None, header=True)
stds_rows.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Row_stds.csv',  index=None, header=True)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))