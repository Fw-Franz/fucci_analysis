import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="Y:\\Juanita\\NewMethodAnalysisSheets\\1_13_21Allsheets\\NoPrimary\\HDAC_NSE_SOX10_Ki67_MAP2_O4_CREB_pH3_nopri\\08_07_2021"

threshold_value=20

root = tk.Tk()
root.withdraw()

#region Input parameters
input_dir_base = filedialog.askdirectory(initialdir=Custom_dir,
# input_dir_base = filedialog.askdirectory(initialdir=BASE_DIR,
                title="Select Antibody Results Directory")
dir_list = os.listdir(input_dir_base)
# endregion

start_time = time.time()

for input_dir in dir_list:

    print('processing ', input_dir)
    print('--------------------')

    sub_dir= input_dir_base + '/' + input_dir + '/'# you can just write this as << save_dir = input_dir_base  >> if you want to save it in the same base directory as the input files, otherweise specify other directory

    input_fname_GFAP="/GFAP.csv" # needs "/" in front
    input_fname_nuclei="/Nuclei.csv" # needs "/" in front

    df=pd.read_csv(sub_dir+input_fname_GFAP)
    df_nuclei=pd.read_csv(sub_dir+input_fname_nuclei)

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

    df.to_csv(path_or_buf=sub_dir + 'GFAP_' + str(threshold_value) + '_Thresholded.csv',  index=None, header=True)
    df_nuclei.to_csv(path_or_buf=sub_dir + 'Nuclei_' + str(threshold_value) + '_Thresholded.csv',  index=None, header=True)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))