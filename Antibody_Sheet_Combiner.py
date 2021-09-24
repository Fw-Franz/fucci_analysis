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
Custom_dir="E:\\3_13_BrdUnewanalysis"


#endregion

root = tk.Tk()
root.withdraw()

input_dir_base = filedialog.askdirectory(initialdir=Custom_dir,
# input_dir_base = filedialog.askdirectory(initialdir=BASE_DIR,
                title="Select DiBAC Results Directory")
combined_dir=input_dir_base+"/combined_sheets"
if not os.path.exists(combined_dir):
    os.makedirs(combined_dir)

# dir_list = os.listdir(input_dir_base)
dir_list=glob.glob(input_dir_base+'**//*BrdU*')

start_time = time.time()

for input_dir in dir_list:

    print('processing ', input_dir)
    print('--------------------')



    input_fname_Experiment="/Experiment.csv" # needs "/" in front
    input_fname_FilteredNuclei="/FilteredNuclei.csv" # needs "/" in front
    input_fname_GFAP="/GFAP.csv" # needs "/" in front
    input_fname_Image="/Image.csv" # needs "/" in front
    input_fname_Nuclei="/Nuclei.csv" # needs "/" in front
    input_fname_PositiveCells="/PositiveCells.csv" # needs "/" in front


    if input_dir==dir_list[0]:
        df_Experiment=pd.read_csv(input_dir+input_fname_Experiment)
        df_FilteredNuclei=pd.read_csv(input_dir+input_fname_FilteredNuclei)
        df_GFAP=pd.read_csv(input_dir+input_fname_GFAP)
        df_Image=pd.read_csv(input_dir+input_fname_Image)
        df_Nuclei=pd.read_csv(input_dir+input_fname_Nuclei)
        df_PositiveCells=pd.read_csv(input_dir+input_fname_PositiveCells)
    else:
        mi_Experiment=pd.read_csv(input_dir+input_fname_Experiment)
        df_Experiment = df_Experiment.append(mi_Experiment)
        mi_FilteredNuclei=pd.read_csv(input_dir+input_fname_FilteredNuclei)
        df_FilteredNuclei = df_FilteredNuclei.append(mi_FilteredNuclei)
        mi_GFAP=pd.read_csv(input_dir+input_fname_GFAP)
        df_GFAP = df_GFAP.append(mi_GFAP)
        mi_Image=pd.read_csv(input_dir+input_fname_Image)
        df_Image = df_Image.append(mi_Image)
        mi_Nuclei=pd.read_csv(input_dir+input_fname_Nuclei)
        df_Nuclei = df_Nuclei.append(mi_Nuclei)
        mi_PositiveCells=pd.read_csv(input_dir+input_fname_PositiveCells)
        df_PositiveCells = df_PositiveCells.append(mi_PositiveCells)


df_Experiment.to_csv(path_or_buf=combined_dir + '\\Experiment.csv',  index=None, header=True)
df_FilteredNuclei.to_csv(path_or_buf=combined_dir + '\\FilteredNuclei.csv',  index=None, header=True)
df_GFAP.to_csv(path_or_buf=combined_dir + '\\GFAP.csv',  index=None, header=True)
df_Image.to_csv(path_or_buf=combined_dir + '\\Image.csv',  index=None, header=True)
df_Nuclei.to_csv(path_or_buf=combined_dir + '\\Nuclei.csv',  index=None, header=True)
df_PositiveCells.to_csv(path_or_buf=combined_dir + '\\PositiveCells.csv',  index=None, header=True)


print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))