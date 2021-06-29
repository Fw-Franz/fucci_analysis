import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\Fucci_analysis\\NG108_FUCCI_Used\\all_data_together"

day=6
pval_min=None # decimal value (0.0xx)  or set to None for all data

root = tk.Tk()
root.withdraw()

# mtukey_filepath = filedialog.askopenfilename(initialdir=Custom_dir,
mtukey_filepath = filedialog.askopenfilename(initialdir=BASE_DIR,
                title="Select Tukey file",
                multiple=False,
                filetypes=(("csv", "*.csv"),))

start_time = time.time()

mtukey=pd.read_csv(mtukey_filepath)

mtukey=mtukey.drop_duplicates()

mtukey=mtukey.loc[mtukey.Day==day]

if not pval_min == None:
    mtukey=mtukey.loc[mtukey["p-adj"]<pval_min]
    mtukey_filepath=mtukey_filepath.replace("tukey_results","tukey_parsed_results_day_"+str(day)+"_"+str(pval_min).replace(".","p"))

else:
    mtukey_filepath = mtukey_filepath.replace("tukey_results", "tukey_parsed_results_day_" + str(day))

mtukey.to_csv(mtukey_filepath, index=False)

print("Total time passed in s: %s" % round((time.time() - start_time), 2))

