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

x=20
y=49345

Custom_dir="D:\\Data_Lab\\Juanita\\Antibody_data\\cmycbestsettings\\"

root = tk.Tk()
root.withdraw()
filepath = filedialog.askopenfilename(
    # initialdir="BASE_DIR",
    initialdir="Custom_dir",
    title="Select file",
    filetypes=(("csv", "*.csv"),)
)


base_directory = os.path.dirname(os.path.dirname(filepath))

df = pd.read_csv(filepath)

df.drop(df.index[x:y], inplace=True)

save_filepath=filepath.replace('.csv','_shortened.csv')
df.to_csv(
    path_or_buf=save_filepath,
    index=None,
    header=True
)