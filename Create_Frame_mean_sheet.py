import tkinter as tk
from tkinter import filedialog
import pandas as pd
import data_annotation
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="C:\\Users\\Franz\\OneDrive\\_PhD\\Juanita\\Fucci_analysis\\NG108_FUCCI_Used\\all_data_together"

root = tk.Tk()
root.withdraw()

# m1_filepath,m2_filepath = filedialog.askopenfilename(initialdir=Custom_dir,
m1_filepath,m2_filepath = filedialog.askopenfilename(initialdir=BASE_DIR,
                title="Select files m1 and m2",
                multiple=True,
                filetypes=(("csv", "*.csv"),))

data1 = data_annotation.AnnotatedData([m1_filepath])
data1.load_annotated_files()
data1.set_normalization('Total', 'Control_DMSO')
m1 = data1.dataframe

data2 = data_annotation.AnnotatedData([m2_filepath])
data2.load_annotated_files()
data2.set_normalization('Total', 'Control_DMSO')
m2 = data2.dataframe

# m1=pd.read_csv(m1_filepath)
# m2=pd.read_csv(m2_filepath)
# m2=m2.set_normalization('Total', 'Control_DMSO')

m_mean_inter=pd.concat([m1,m2])

m_mean=m_mean_inter.groupby(['PlateNum', 'WellNum', 'Day', 'Marker','Condition','PlateRow','PlateColumn','Date'], sort = False).mean()
m_mean["Frame"]="ean"

m_mean_filepath=m1_filepath.replace("_m1_","_mean_")
print(m_mean_filepath)
m_mean.to_csv(m_mean_filepath, index=True)

# print(m_mean)