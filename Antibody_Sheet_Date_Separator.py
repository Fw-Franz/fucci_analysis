import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import os
import glob

# pd.set_option('mode.chained_assignment', 'raise')
pd.set_option('mode.chained_assignment', None)

#region Input parameters
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\pH3Redos_Results\\ph3_3_13_and_4_13"

search_list=['3_13_21','4_8_21']

column_search_name='PathName_OrigBlue'

#endregion

root = tk.Tk()
root.withdraw()

input_dir = filedialog.askdirectory(initialdir=Custom_dir,
# input_dir_base = filedialog.askdirectory(initialdir=BASE_DIR,
                title="Select Antibody Results Directory")

input_dir_base = os.path.dirname(input_dir)

start_time = time.time()

 # needs "/" in front
input_fname_FilteredNuclei="/FilteredNuclei.csv" # needs "/" in front
input_fname_GFAP="/GFAP.csv" # neeeds "/" in front
input_fname_Nuclei="/Nuclei.csv" # needs "/" in front
input_fname_PositiveCells="/PositiveCells.csv" # needs "/" in front

df_FilteredNuclei=pd.read_csv(input_dir+input_fname_FilteredNuclei)
df_GFAP=pd.read_csv(input_dir+input_fname_GFAP)
df_Nuclei=pd.read_csv(input_dir+input_fname_Nuclei)
df_PositiveCells=pd.read_csv(input_dir+input_fname_PositiveCells)

for search_item in search_list:

    print('processing ', search_item)
    print('--------------------')

    search_save_dir=input_dir_base+"//"+search_item
    if not os.path.exists(search_save_dir):
        os.makedirs(search_save_dir)

    df_FilteredNuclei_sep = df_FilteredNuclei[df_FilteredNuclei[column_search_name].str.contains(search_item)==True]
    df_GFAP_sep = df_GFAP[df_GFAP[column_search_name].str.contains(search_item)==True]
    df_Nuclei_sep = df_Nuclei[df_Nuclei[column_search_name].str.contains(search_item)==True]
    df_PositiveCells_sep = df_PositiveCells[df_PositiveCells[column_search_name].str.contains(search_item)==True]

    df_FilteredNuclei_sep.to_csv(path_or_buf=search_save_dir + '\\FilteredNuclei.csv',  index=None, header=True)
    df_GFAP_sep.to_csv(path_or_buf=search_save_dir + '\\GFAP.csv',  index=None, header=True)
    df_Nuclei_sep.to_csv(path_or_buf=search_save_dir + '\\Nuclei.csv',  index=None, header=True)
    df_PositiveCells_sep.to_csv(path_or_buf=search_save_dir + '\\PositiveCells.csv',  index=None, header=True)


print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))