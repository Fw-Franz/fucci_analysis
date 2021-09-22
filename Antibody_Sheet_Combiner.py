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
Custom_dir="E:\\NG108_staining\\Brdu_Analysis_diffthresh_newest\\12_24realdate"


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
dir_list=glob.glob(input_dir_base+'**//*only*')

start_time = time.time()

for input_dir in dir_list:

    print('processing ', input_dir)
    print('--------------------')


    input_fname_GFAP="/GFAP.csv" # needs "/" in front

    if input_dir==dir_list[0]:
        df=pd.read_csv(input_dir+input_fname_GFAP)
    else:
        mi=pd.read_csv(input_dir+input_fname_GFAP)
        df = df.append(mi)




df.to_csv(path_or_buf=combined_dir + '\\GFAP.csv',  index=None, header=True)


print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))