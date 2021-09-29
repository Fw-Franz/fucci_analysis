import tkinter as tk
from tkinter import filedialog
import time
import os
import glob
import shutil

#region Input parameters
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="E:\\U87_Combo_YAP_backgroundsub\\YAP_BS_2021-09-25-00-50-31_set2"

substrings1=['f'] # leave as [''] if not needed
substrings2=['34','35','36','42','43','44','45','46','52','53','54'] # leave as [''] if not needed

search_string_base = '' # leave as '' if not needed
search_filetype = '*.tif' # leave as '' if not needed
# YAP_BS_Plate_R_p00_0_B02f00d0_gauss_mask_substracted
# it will add like this: **//*'+search_string_base+ substring1 + substring2 +  search_filetype)
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
target_dir=parent_dir+'\\'+os.path.basename(input_dir_base)+"_center_frames/"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

#endregion

# region Move (or copy) files
start_time = time.time()

for substring1 in substrings1:
    for substring2 in substrings2:
        file_list=glob.glob(input_dir_base+'**//*'+search_string_base+ substring1 + substring2 +  search_filetype)
        for file_name in file_list:
            # shutil.move(os.path.join(input_dir_base, file_name), target_dir)
            shutil.copy(os.path.join(input_dir_base, file_name), target_dir)


print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))

#endregion