import os
import pandas as pd
import numpy as np
import seaborn as sns
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib
import matplotlib.pyplot as plt
import time


start_time = time.time()

x=84163
y=183039

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="F:\\NewAnalysisSheetsAll8_29_21\\4_8_21Allsheets_allin\\RegAntibodies\\ERK_HDAC9_MBP_TH\\"

root = tk.Tk()
root.withdraw()
filepath = filedialog.askopenfilename(
    initialdir="BASE_DIR",
    # initialdir="Custom_dir",
    title="Select file",
    filetypes=(("csv", "*.csv"),)
)


base_directory = os.path.dirname(os.path.dirname(filepath))

df = pd.read_csv(filepath)

df.drop(df.index[x-2:y-1], inplace=True)

save_filepath=filepath.replace('.csv','_shortened.csv')
df.to_csv(
    path_or_buf=save_filepath,
    index=None,
    header=True
)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))