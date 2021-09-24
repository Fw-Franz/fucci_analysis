import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import os

# pd.set_option('mode.chained_assignment', 'raise')
pd.set_option('mode.chained_assignment', None)

#region Input parameters
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Custom_dir="Y:\\Juanita\\NewMethodAnalysisSheets\\1_13_21Allsheets\\RegAntibodies\\CMYC_cx43_cx46_GFAP_HDAC9_MAP2\\08_07_2021"
Current_dir=os.getcwd()

input_folder_name=os.path.basename(Current_dir)

row_B_drug_name='Drug_A'
row_C_drug_name='Drug_B'
row_D_drug_name='Drug_C'
row_E_drug_name='Control'
row_F_drug_name='Drug_D'
row_G_drug_name='Drug_E'

#endregion

root = tk.Tk()
root.withdraw()

# input_dir_base = filedialog.askdirectory(initialdir=Custom_dir,
# # input_dir_base = filedialog.askdirectory(initialdir=BASE_DIR,
#                 title="Select Antibody Results Directory")
# dir_list = os.listdir(input_dir_base)

start_time = time.time()

sub_dir= Current_dir

input_fname_nuclei="/Nuclei.csv" # needs "/" in front

df_nuclei=pd.read_csv(sub_dir+input_fname_nuclei)


image_n=df_nuclei.ImageNumber.tolist()# total number of wells
image_n = list(dict.fromkeys(image_n))

mi=df_nuclei[['ImageNumber','ObjectNumber','FileName_DisplayImage','Classify_PH3Pos',
           'Classify_PH3neg']]
mi=mi.rename(columns={"Classify_PH3Pos": "Ph3_positive",
                      "Classify_PH3neg": "Ph3_negative"})

mi['Cell_Num']=mi.groupby(by='ImageNumber')['ImageNumber'].transform('count')
mi_pos=mi[mi.Classify_PH3Pos==1]
mi['Cell_Num_Positive']=mi_pos.groupby(by='ImageNumber')['ImageNumber'].transform('count')

name = df_nuclei['FileName_DisplayImage'].values[0]

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
mi['Cell_Num_Positive'] = mi['Cell_Num_Positive'].astype(float)

means_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).mean()
stds_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).std()

means_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).mean()
stds_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).std()

inter_means = means_frame.groupby(['Row', 'Column'], as_index=False).sum()

means_columns['Cell_Num'] = inter_means['Cell_Num']
means_columns['Cell_Num_Positive'] = inter_means['Cell_Num_Positive']
means_columns['Cell_Percent_Positive'] = means_columns['Cell_Num_Positive'] / means_columns['Cell_Num']

means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()

means_rows_control=means_rows.loc[means_rows.Drug_Name=='Control']


means_columns['Fold_change_Cell_Num'] = means_columns['Cell_Num'].copy()/float(means_rows_control['Cell_Num'])
means_columns['Fold_change_Cell_Num_Positive'] = means_columns['Cell_Num_Positive'].copy()/float(means_rows_control['Cell_Num_Positive'])
means_columns['Fold_change_Cell_Percent_Positive'] = means_columns['Cell_Percent_Positive'].copy()/float(means_rows_control['Cell_Percent_Positive'])

means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()

mi.to_csv(path_or_buf=sub_dir + '\\' +input_folder_name + '_AntibodyResults.csv',  index=None, header=True)

means_frame.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_BRDU_Results_Frame_means.csv',  index=None, header=True)
means_columns.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_BRDU_Results_Column_means.csv',  index=None, header=True)
means_rows.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_BRDU_Results_Row_means.csv',  index=None, header=True)

stds_frame.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_BRDU_Results_Frame_stds.csv',  index=None, header=True)
stds_columns.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_BRDU_Results_Column_stds.csv',  index=None, header=True)
stds_rows.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_BRDU_Results_Row_stds.csv',  index=None, header=True)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))