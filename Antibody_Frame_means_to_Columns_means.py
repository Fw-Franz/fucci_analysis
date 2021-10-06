import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import os
import glob

# pd.set_option('mode.chained_assignment', 'raise')
pd.set_option('mode.chained_assignment', None)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir=r"E:\YAP_Perinuc_analysis_set1_center\\"
root = tk.Tk()
root.withdraw()

# base_directory = filedialog.askdirectory(initialdir=BASE_DIR,
base_directory = filedialog.askdirectory(initialdir=Custom_dir,
                title="Select Antibody Results Directory")

start_time = time.time()

filepath_means = glob.glob(base_directory + '**/*Frame_means_Outlier_removed.csv')

input_folder_name = os.path.basename(base_directory)

means_frames=pd.read_csv(filepath_means[0])

means_frames=means_frames.drop(columns=['Frame'])

means_columns=means_frames.groupby(['Column','Row','Drug_Name'], as_index=False).mean()
stds_columns=means_frames.groupby(['Column','Row','Drug_Name'], as_index=False).std()

means_columns.to_csv(path_or_buf=base_directory + '\\'+ input_folder_name + '_Thresholded_AntibodyResults_Column_means.csv',  index=None, header=True)

stds_columns.to_csv(path_or_buf=base_directory + '\\'+ input_folder_name + '_Thresholded_AntibodyResults_Column_stds.csv',  index=None, header=True)


means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()

means_rows.to_csv(path_or_buf=base_directory + '\\'+ input_folder_name + '_Thresholded_AntibodyResults_Row_means.csv',  index=None, header=True)

stds_rows.to_csv(path_or_buf=base_directory + '\\'+ input_folder_name + '_Thresholded_AntibodyResults_Row_stds.csv',  index=None, header=True)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))