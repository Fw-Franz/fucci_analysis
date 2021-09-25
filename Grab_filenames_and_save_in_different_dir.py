import tkinter as tk
from tkinter import filedialog
import time
import os
import glob
import shutil

#region Input parameters
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="E:\\U87_RetPant_pHist3MeanInt"

substrings1=['Hist3_BS_Plate_R'] # leave as [''] if not needed
substrings2=[''] # leave as [''] if not needed

search_string_base = '' # leave as '' if not needed
search_filetype = '*.tiff' # leave as '' if not needed

# substrings1=['02','03','04',] # leave as [''] if not needed
# substrings2=['B','C','D','E','F','G'] # leave as [''] if not needed
#
# search_string_base = 'R_p00_0_' # leave as '' if not needed
# search_filetype = '*.tif' # leave as '' if not needed

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
target_dir=parent_dir+'\\'+os.path.basename(input_dir_base)+"_Hist3/"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

#endregion

# region Move (or copy) files
start_time = time.time()

for substring1 in substrings1:
    for substring2 in substrings2:
        file_list=glob.glob(input_dir_base+'**//*'+search_string_base+ substring2 + substring1+ search_filetype)
        for file_name in file_list:
            shutil.move(os.path.join(input_dir_base, file_name), target_dir)
            # shutil.copy(os.path.join(input_dir_base, file_name), target_dir)


print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))

#endregion