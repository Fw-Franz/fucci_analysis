import pandas as pd
import tkinter as tk
from tkinter import filedialog
import time
import os

pd.options.mode.chained_assignment = None # None|warn|raise

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


    input_fname_Ki67nuc="/Ki67nuc.csv" # needs "/" in front
    input_fname_nuclei="/Nuclei.csv" # needs "/" in front
    input_fname_positive_cells="/PositiveCells.csv" # needs "/" in front

    print('loading data ... ')
    df=pd.read_csv(sub_dir++input_fname_Ki67nuc)
    df_nuclei=pd.read_csv(sub_dir+input_fname_nuclei)
    df_positive=pd.read_csv(sub_dir+input_fname_positive_cells)

    image_n=df.ImageNumber.tolist()# total number of wells
    image_n = list(dict.fromkeys(image_n))
    print(type(image_n))

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

    print('row, col, frame: ', row, col, frame)

    mi['Row']=mi.FileName_DisplayImage.str.slice(base_postion + 9, base_postion + 10)
    mi['Column']=mi.FileName_DisplayImage.str.slice(base_postion + 10, base_postion + 12)
    mi['Frame']=mi.FileName_DisplayImage.str.slice(base_postion + 12, base_postion + 15)

    mi_pos['Row']=mi_pos.FileName_DisplayImage.str.slice(base_postion + 9, base_postion + 10)
    mi_pos['Column']=mi_pos.FileName_DisplayImage.str.slice(base_postion + 10, base_postion + 12)
    mi_pos['Frame']=mi_pos.FileName_DisplayImage.str.slice(base_postion + 12, base_postion + 15)

    mi=mi.drop(columns=['FileName_DisplayImage'])

    mi['DAPI_area'] = mi['DAPI_area'].astype(float)
    mi['FarRed_area'] = mi['FarRed_area'].astype(float)
    mi['Cell_Num'] = mi['Cell_Num'].astype(float)

    means_frame=mi.groupby(['Row', 'Column', 'Frame'], as_index=False).mean()
    stds_frame=mi.groupby(['Row', 'Column', 'Frame'], as_index=False).std()

    means_pos_frame=mi_pos.groupby(['Row', 'Column', 'Frame'], as_index=False).mean()
    stds_pos_frame=mi_pos.groupby(['Row', 'Column', 'Frame'], as_index=False).std()

    means_columns=means_frame.groupby(['Row', 'Column'], as_index=False).mean()
    stds_columns=means_frame.groupby(['Row', 'Column'], as_index=False).std()

    inter_means=means_frame.groupby(['Row', 'Column'], as_index=False).sum()
    inter_means_pos=means_pos_frame.groupby(['Row', 'Column'], as_index=False).sum()

    means_columns['Cell_Num']=inter_means['Cell_Num']
    means_columns['Cell_Num_Positive']=inter_means_pos['Cell_Num_Positive']
    means_columns['Cell_Percent_Positive']=means_columns['Cell_Num_Positive']/means_columns['Cell_Num']

    means_rows=means_columns.groupby(['Row'], as_index=False).mean()
    stds_rows=means_columns.groupby(['Row'], as_index=False).std()

    mi.to_csv(path_or_buf=sub_dir +input_dir + '_AntibodyResults.csv',  index=None, header=True)

    means_frame.to_csv(path_or_buf=sub_dir + input_dir + '_AntibodyResults_Frame_means.csv',  index=None, header=True)
    means_columns.to_csv(path_or_buf=sub_dir + input_dir + '_AntibodyResults_Column_means.csv',  index=None, header=True)
    means_rows.to_csv(path_or_buf=sub_dir + input_dir + '_AntibodyResults_Row_means.csv',  index=None, header=True)

    stds_frame.to_csv(path_or_buf=sub_dir + input_dir + '_AntibodyResults_Frame_stds.csv',  index=None, header=True)
    stds_columns.to_csv(path_or_buf=sub_dir + input_dir + '_AntibodyResults_Column_stds.csv',  index=None, header=True)
    stds_rows.to_csv(path_or_buf=sub_dir + input_dir + '_AntibodyResults_Row_stds.csv',  index=None, header=True)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))