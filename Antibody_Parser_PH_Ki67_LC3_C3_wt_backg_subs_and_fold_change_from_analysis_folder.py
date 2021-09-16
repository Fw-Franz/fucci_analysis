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



Antibody_type= 'PhosHist' # 'PhosHist' , 'Ki67' , 'LC3' , or 'CASP3'

row_B_FarRed_int_I_background_average=0
row_C_FarRed_int_I_background_average=0
row_D_FarRed_int_I_background_average=0
row_E_FarRed_int_I_background_average=0
row_F_FarRed_int_I_background_average=0
row_G_FarRed_int_I_background_average=0

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

if Antibody_type == 'PhosHist':
    input_fname_GFAP="/GFAP.csv"
if Antibody_type == 'Ki67':
    input_fname_GFAP = "/Ki67nuc.csv"
if Antibody_type == 'LC3':
    input_fname_GFAP="/GFAP.csv"
if Antibody_type == 'CASP3':
    input_fname_GFAP = "/GFAP.csv"


input_fname_nuclei="/Nuclei.csv" # needs "/" in front
input_fname_positive_cells="/PositiveCells.csv" # needs "/" in front

df=pd.read_csv(sub_dir+input_fname_GFAP)
df_nuclei=pd.read_csv(sub_dir+input_fname_nuclei)
df_positive=pd.read_csv(sub_dir+input_fname_positive_cells)

print('pre threshold GFAP # rows: ', df.shape[0], '\npre threshold nuclei # rows: ', df_nuclei.shape[0])

image_n=df.ImageNumber.tolist()# total number of wells
image_n = list(dict.fromkeys(image_n))

df['row_id'] =  '_' + df['ImageNumber'].apply(str) + 'and' + df['ObjectNumber'].apply(str) + '_'

df_nuclei['row_id'] =  '_' + df_nuclei['ImageNumber'].apply(str) + 'and' + df_nuclei['ObjectNumber'].apply(str) + '_'
df_nuclei['test'] = df_nuclei['row_id'].isin(df[  'row_id'])
df_nuclei = df_nuclei[df_nuclei.test == True]
df_nuclei = df_nuclei.reset_index(drop=True)
df_nuclei.drop(columns=['test'], inplace=True)

print('post threshold GFAP # rows: ', df.shape[0], '\npost threshold nuclei # rows: ', df_nuclei.shape[0], '\n')

mi=df[['ImageNumber','ObjectNumber','FileName_DisplayImage','Intensity_IntegratedIntensity_OrigBlue',
           'Intensity_IntegratedIntensity_OrigGreen','Intensity_MeanIntensity_OrigGreen',
       'Intensity_MeanIntensity_OrigBlue','AreaShape_Area']]
mi=mi.rename(columns={"Intensity_IntegratedIntensity_OrigBlue": "DAPI_int_I",
                      "Intensity_IntegratedIntensity_OrigGreen": "FarRed_int_I",
                      "Intensity_MeanIntensity_OrigGreen": "FarRed_mean_I",
                      "Intensity_MeanIntensity_OrigBlue": "DAPI_mean_I",
                      "AreaShape_Area": "FarRed_area"})
mi['DAPI_area']=df_nuclei['AreaShape_Area']

mi['Cell_Num']=mi.groupby(by='ImageNumber')['ImageNumber'].transform('count')

mi_pos=df_positive[['ImageNumber','ObjectNumber','FileName_DisplayImage']]

mi_pos['Cell_Num_Positive']=mi_pos.groupby(by='ImageNumber')['ImageNumber'].transform('count')

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

mi['DAPI_area'] = mi['DAPI_area'].astype(float)
mi['FarRed_area'] = mi['FarRed_area'].astype(float)
mi['Cell_Num'] = mi['Cell_Num'].astype(float)

means_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).mean()
stds_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).std()

means_pos_frame = mi_pos.groupby(['Row', 'Column', 'Frame'], as_index=False).mean()
stds_pos_frame = mi_pos.groupby(['Row', 'Column', 'Frame'], as_index=False).std()

means_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).mean()
stds_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).std()

background_sub_df = pd.DataFrame(data=[row_B_FarRed_int_I_background_average, row_C_FarRed_int_I_background_average,
                                       row_D_FarRed_int_I_background_average, row_E_FarRed_int_I_background_average,
                                       row_F_FarRed_int_I_background_average,
                                       row_G_FarRed_int_I_background_average],
                                 index=None, columns=['FarRed_int_I_background_average'])

means_columns['FarRed_int_I_background_average']=means_columns['Row'].copy()
means_columns['FarRed_int_I_background_average'].loc[means_columns.Row=='B']=row_B_FarRed_int_I_background_average
means_columns['FarRed_int_I_background_average'].loc[means_columns.Row=='C']=row_C_FarRed_int_I_background_average
means_columns['FarRed_int_I_background_average'].loc[means_columns.Row=='D']=row_D_FarRed_int_I_background_average
means_columns['FarRed_int_I_background_average'].loc[means_columns.Row=='E']=row_E_FarRed_int_I_background_average
means_columns['FarRed_int_I_background_average'].loc[means_columns.Row=='F']=row_F_FarRed_int_I_background_average
means_columns['FarRed_int_I_background_average'].loc[means_columns.Row=='G']=row_G_FarRed_int_I_background_average

inter_means = means_frame.groupby(['Row', 'Column'], as_index=False).sum()
inter_means_pos = means_pos_frame.groupby(['Row', 'Column'], as_index=False).sum()

means_columns['Cell_Num'] = inter_means['Cell_Num']
means_columns['Cell_Num_Positive'] = inter_means_pos['Cell_Num_Positive']
means_columns['Cell_Percent_Positive'] = means_columns['Cell_Num_Positive'] / means_columns['Cell_Num']

# means_columns['FarRed_int_I_background_sub']=means_columns['FarRed_int_I'].copy()
means_columns['FarRed_int_I_background_sub']=means_columns['FarRed_int_I'].copy()-means_columns['FarRed_int_I_background_average'].copy()
# stds_columns['FarRed_int_I_background_sub']=stds_columns['FarRed_int_I']-background_sub_df['FarRed_int_I_background_average']


means_columns['FarRed_int_I_background_average'] = means_columns['FarRed_int_I_background_average'].astype(float)
means_columns['FarRed_int_I_background_sub'] = means_columns['FarRed_int_I_background_sub'].astype(float)

means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()


# 'DAPI_int_I', "FarRed_int_I", "FarRed_mean_I", "DAPI_mean_I", "FarRed_area", "DAPI_area"

means_rows_control=means_rows.loc[means_rows.Drug_Name=='Control']

means_columns['Fold_change_DAPI_int_I']=means_columns['DAPI_int_I'].copy()/float(means_rows_control['DAPI_int_I'])
means_columns['Fold_change_FarRed_int_I']=means_columns['FarRed_int_I'].copy()/float(means_rows_control['FarRed_int_I'])
means_columns['Fold_change_FarRed_int_I_background_sub']=means_columns['FarRed_int_I_background_sub'].copy()/float(means_rows_control['FarRed_int_I_background_sub'])
means_columns['Fold_change_FarRed_mean_I']=means_columns['FarRed_mean_I'].copy()/float(means_rows_control['FarRed_mean_I'])
means_columns['Fold_change_DAPI_mean_I']=means_columns['DAPI_mean_I'].copy()/float(means_rows_control['DAPI_mean_I'])
means_columns['Fold_change_FarRed_area']=means_columns['FarRed_area'].copy()/float(means_rows_control['FarRed_area'])
means_columns['Fold_change_DAPI_area']=means_columns['DAPI_area'].copy()/float(means_rows_control['DAPI_area'])
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