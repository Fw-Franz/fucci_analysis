import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="D:\hisc_data"

root = tk.Tk()
root.withdraw()

mi_filepath = filedialog.askopenfilename(initialdir=Custom_dir,
# mi_filepath = filedialog.askopenfilename(initialdir=BASE_DIR,
                title="Select data file to get fucci differences",
                multiple=False,
                filetypes=(("csv", "*.csv"),))

mi=pd.read_csv(mi_filepath)

mi_control=mi.loc[mi.Condition=='Control_DMSO']
control_means=np.mean(mi_control)


mi.Total=mi.Total/control_means.Total
mi.Alive=mi.Alive/control_means.Alive
mi.Dead=mi.Dead/control_means.Dead
mi.Percent_Alive=mi.Percent_Alive/control_means.Percent_Alive
mi.Percent_Dead=mi.Percent_Dead/control_means.Percent_Dead

mi_filepath_save = mi_filepath.replace('M1_Processed_All', 'M1_Processed_All_normalized')

mi.reset_index(inplace=True)
mi.to_csv(mi_filepath_save)
