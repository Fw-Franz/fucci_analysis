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

row_B_drug_name='Control'
row_C_drug_name='1perFBS_cAMP_1mM_Rapamycin_200nM'
row_D_drug_name='Pantoprazole_100uM'
row_E_drug_name='Pantoprazole_100uM_NS1643_50uM'
row_F_drug_name='Pantoprazole_100uM_TMZ_50uM'
row_G_drug_name='NS1643_50uM_100uM_TMZ_50uM'

#endregion

root = tk.Tk()
root.withdraw()

# input_dir_base = filedialog.askdirectory(initialdir=Custom_dir,
# # input_dir_base = filedialog.askdirectory(initialdir=BASE_DIR,
#                 title="Select Antibody Results Directory")
# dir_list = os.listdir(input_dir_base)

start_time = time.time()

sub_dir= Current_dir


input_fname_GFAP = "/GFAP.csv"
input_fname_nuclei="/Nuclei.csv" # needs "/" in front
input_fname_positive_cells="/PositiveCells.csv" # needs "/" in front

df=pd.read_csv(sub_dir+input_fname_GFAP)
df_nuclei=pd.read_csv(sub_dir+input_fname_nuclei)
df_positive=pd.read_csv(sub_dir+input_fname_positive_cells)

image_n=df.ImageNumber.tolist()# total number of wells
image_n = list(dict.fromkeys(image_n))

mi=df[['ImageNumber','ObjectNumber','FileName_DisplayImage']]

mi['Cell_Num']=mi.groupby(by='FileName_DisplayImage')['FileName_DisplayImage'].transform('count')

mi_pos=df_positive[['ImageNumber','ObjectNumber','FileName_DisplayImage']]

mi_pos['Cell_Num_Positive']=mi_pos.groupby(by='FileName_DisplayImage')['FileName_DisplayImage'].transform('count')

name = df['FileName_DisplayImage'].values[0]

base_postion = name.find("_R_", 0, len(name))
row = name[base_postion + 9]
col = name[base_postion + 10:base_postion + 12]
frame = name[base_postion + 12:base_postion + 15]

print('row, col, frame: ', row, col, frame, '\n')

mi['Row']=mi.FileName_DisplayImage.str.slice(base_postion + 9, base_postion + 10)
mi['Column']=mi.FileName_DisplayImage.str.slice(base_postion + 10, base_postion + 12)
mi['Frame']=mi.FileName_DisplayImage.str.slice(base_postion + 12, base_postion + 15)

mi_pos['Row']=mi_pos.FileName_DisplayImage.str.slice(base_postion + 9, base_postion + 10)
mi_pos['Column']=mi_pos.FileName_DisplayImage.str.slice(base_postion + 10, base_postion + 12)
mi_pos['Frame']=mi_pos.FileName_DisplayImage.str.slice(base_postion + 12, base_postion + 15)

mi=mi.drop(columns=['FileName_DisplayImage'])

mi['Drug_Name']=mi['Row'].copy()
mi['Drug_Name'].loc[mi.Drug_Name=='B']=row_B_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='C']=row_C_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='D']=row_D_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='E']=row_E_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='F']=row_F_drug_name
mi['Drug_Name'].loc[mi.Drug_Name=='G']=row_G_drug_name

mi['Cell_Num'] = mi['Cell_Num'].astype(float)

means_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).mean()
stds_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).std()

means_pos_frame = mi_pos.groupby(['Row', 'Column', 'Frame'], as_index=False).mean()
stds_pos_frame = mi_pos.groupby(['Row', 'Column', 'Frame'], as_index=False).std()

means_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).mean()
stds_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).std()

inter_means = means_frame.groupby(['Row', 'Column'], as_index=False).sum()
inter_means_pos = means_pos_frame.groupby(['Row', 'Column'], as_index=False).sum()

means_columns['Cell_Num'] = inter_means['Cell_Num']
means_columns['Cell_Num_Positive']=0
for row in means_columns['Row'].unique():
    for column in means_columns['Column'].unique():
        if len(inter_means_pos.loc[(inter_means_pos.Row==row)&(inter_means_pos.Column==column),['Cell_Num_Positive']])>0:
            means_columns.loc[(means_columns.Row==row)&(means_columns.Column==column),['Cell_Num_Positive']] = inter_means_pos.loc[(inter_means_pos.Row==row)&(inter_means_pos.Column==column),['Cell_Num_Positive']].values[0]

means_columns['Cell_Percent_Positive'] = means_columns['Cell_Num_Positive'] / means_columns['Cell_Num']

means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()


# 'DAPI_int_I', "FarRed_int_I", "FarRed_mean_I", "DAPI_mean_I", "FarRed_area", "DAPI_area"

means_rows_control=means_rows.loc[means_rows.Drug_Name=='Control']

means_columns['Fold_change_Cell_Percent_Positive'] = means_columns['Cell_Percent_Positive'].copy()/float(means_rows_control['Cell_Percent_Positive'])

means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()

mi.to_csv(path_or_buf=sub_dir + '\\' +input_folder_name + '_AntibodyResults.csv',  index=None, header=True)

means_frame.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Frame_means.csv',  index=None, header=True)
means_columns.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Column_means.csv',  index=None, header=True)
means_rows.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Row_means.csv',  index=None, header=True)

stds_frame.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Frame_stds.csv',  index=None, header=True)
stds_columns.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Column_stds.csv',  index=None, header=True)
stds_rows.to_csv(path_or_buf=sub_dir + '\\'+ input_folder_name + '_AntibodyResults_Row_stds.csv',  index=None, header=True)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))