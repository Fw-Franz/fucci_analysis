import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import os
import glob

# pd.set_option('mode.chained_assignment', 'raise')
pd.set_option('mode.chained_assignment', None)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Custom_dir="E:\\NewAnalysisSheetsAll8_29_21\\2_2_21Allsheets_allin\\RegAntibodies\\cx43_cx46_GFAP_HDAC9_MAP2\\08_07_2021\\"
root = tk.Tk()
root.withdraw()

base_directory = filedialog.askdirectory(initialdir=BASE_DIR,
                title="Select Antibody Results Directory")

start_time = time.time()

filepath_means = glob.glob(base_directory + '**/*Thresholded_AntibodyResults_Column_means.csv')
filepath_stds = glob.glob(base_directory + '**/*Thresholded_AntibodyResults_Column_stds.csv')

input_folder_name = os.path.basename(base_directory)

means_columns=pd.read_csv(filepath_means[0])
stds_columns=pd.read_csv(filepath_stds[0])

means_columns=means_columns.drop(columns=['Column'])
stds_columns=stds_columns.drop(columns=['Column'])

means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()

means_rows.to_csv(path_or_buf=base_directory + '\\'+ input_folder_name + '_Thresholded_AntibodyResults_Row_means.csv',  index=None, header=True)

stds_rows.to_csv(path_or_buf=base_directory + '\\'+ input_folder_name + '_Thresholded_AntibodyResults_Row_stds.csv',  index=None, header=True)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))