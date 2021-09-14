import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import os

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="T:\\Juanita\\NewMethodAnalysisSheets\\U87Allsheets\\no primary\\\MOG_nopri"

threshold_value=70

root = tk.Tk()
root.withdraw()

#region Input parameters
input_dir = filedialog.askdirectory(initialdir=Custom_dir,
# input_dir_base = filedialog.askdirectory(initialdir=BASE_DIR,
                title="Select Antibody Results Directory")
input_folder_name=os.path.basename(input_dir)

# endregion

start_time = time.time()

print('processing ', input_dir)
print('--------------------')

input_fname_GFAP="/GFAP.csv" # needs "/" in front
input_fname_nuclei="/Nuclei.csv" # needs "/" in front

df=pd.read_csv(input_dir+input_fname_GFAP)
df_nuclei=pd.read_csv(input_dir+input_fname_nuclei)

print('pre threshold GFAP # rows: ', df.shape[0], '\npre threshold nuclei # rows: ', df_nuclei.shape[0])

image_n=df.ImageNumber.tolist()# total number of wells
image_n = list(dict.fromkeys(image_n))

df_shape_base=df.shape
df = df[df.Intensity_IntegratedIntensity_OrigGreen < threshold_value]
df_shape_post = df.shape
df= df.reset_index(drop=True)

print("Number of removed rows GFAP: ", df_shape_base[0]-df_shape_post[0])

df['row_id'] =  '_' + df['ImageNumber'].apply(str) + 'and' + df['ObjectNumber'].apply(str) + '_'
df_nuclei['row_id'] =  '_' + df_nuclei['ImageNumber'].apply(str) + 'and' + df_nuclei['ObjectNumber'].apply(str) + '_'

df_nuclei['test'] = df_nuclei['row_id'].isin(df['row_id'])
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

name = df['FileName_DisplayImage'].values[0]

base_postion = name.find("_R_", 0, len(name))
row = name[base_postion + 9]
col = name[base_postion + 10:base_postion + 12]
frame = name[base_postion + 12:base_postion + 15]

print('row, col, frame: ', row, col, frame, '\n')

mi['Row']=mi.FileName_DisplayImage.str.slice(base_postion + 9, base_postion + 10)
mi['Column']=mi.FileName_DisplayImage.str.slice(base_postion + 10, base_postion + 12)
mi['Frame']=mi.FileName_DisplayImage.str.slice(base_postion + 12, base_postion + 15)

mi=mi.drop(columns=['FileName_DisplayImage'])

mi['DAPI_area'] = mi['DAPI_area'].astype(float)
mi['FarRed_area'] = mi['FarRed_area'].astype(float)
mi['Cell_Num'] = mi['Cell_Num'].astype(float)

means_frame=mi.groupby(['Row', 'Column', 'Frame'], as_index=False).mean()
stds_frame=mi.groupby(['Row', 'Column', 'Frame'], as_index=False).std()

means_columns=means_frame.groupby(['Row', 'Column'], as_index=False).mean()
stds_columns=means_frame.groupby(['Row', 'Column'], as_index=False).std()

means_rows=means_columns.groupby(['Row'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row'], as_index=False).std()

mi.to_csv(path_or_buf=input_dir + '\\'+input_folder_name+ '_' + str(threshold_value) + '_Thresholded_AntibodyResults.csv',  index=None, header=True)

means_frame.to_csv(path_or_buf= input_dir + '\\'+input_folder_name+ '_' + str(threshold_value) + '_Thresholded_AntibodyResults_Frame_means.csv',  index=None, header=True)
means_columns.to_csv(path_or_buf= input_dir + '\\'+input_folder_name+ '_'+ str(threshold_value) + '_Thresholded_AntibodyResults_Column_means.csv',  index=None, header=True)
means_rows.to_csv(path_or_buf=input_dir + '\\'+input_folder_name+ '_' + str(threshold_value) + '_Thresholded_AntibodyResults_Row_means.csv',  index=None, header=True)

stds_frame.to_csv(path_or_buf= input_dir + '\\'+input_folder_name+ '_' + str(threshold_value) + '_Thresholded_AntibodyResults_Frame_stds.csv',  index=None, header=True)
stds_columns.to_csv(path_or_buf= input_dir + '\\'+input_folder_name+ '_' + str(threshold_value) + '_Thresholded_AntibodyResults_Column_stds.csv',  index=None, header=True)
stds_rows.to_csv(path_or_buf= input_dir + '\\'+input_folder_name+ '_' + str(threshold_value) + '_Thresholded_AntibodyResults_Row_stds.csv',  index=None, header=True)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))