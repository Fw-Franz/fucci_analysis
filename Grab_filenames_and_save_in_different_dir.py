import tkinter as tk
from tkinter import filedialog
import time
import os
import glob
import shutil

#region Input parameters
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="F:\\U87dyeassays_Background\\U87DiBac_Background\\U87DiBAC4_3_Day6withdrugafterlast_2021-09-22-23-18-57seperated"

columns=['02','03','04',]
rows=['B','C','D','E','F','G']

#endregion

#region Tkinter File dialogg

# root = tk.Tk()
# root.withdraw()

# input_dir_base = filedialog.askdirectory(initialdir=Custom_dir,
# input_dir_base = filedialog.askdirectory(initialdir=BASE_DIR,
#                 title="Select Directory To Grab From")
#endregion

#region Assemble source and target directories
input_dir_base=Custom_dir
parent_dir = os.path.dirname(input_dir_base)
target_dir=parent_dir+'\\'+os.path.basename(input_dir_base)+"set1/"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

#endregion

# region Move (or copy) files
start_time = time.time()

for column in columns:
    for row in rows:
        file_list=glob.glob(input_dir_base+'**//*R_p00_0_'+ row + column+ '*.tif')
        for file_name in file_list:
            shutil.move(os.path.join(input_dir_base, file_name), target_dir)
            # shutil.copy(os.path.join(input_dir_base, file_name), target_dir)


print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))

#endregion