import tkinter as tk
from tkinter import filedialog
import pandas as pd

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

root = tk.Tk()
root.withdraw()

filepaths = filedialog.askopenfilename(initialdir=BASE_DIR,
                title="Select mean frame files",
                multiple=True,
                filetypes=(("csv", "*.csv"),))

for i in filepaths:
    mi=pd.read_csv(i)
    if i == filepaths[0]:
        m_all=mi.copy()
    else:
        m_all=m_all.append(mi)

filepath_base=filepaths[0]
m_all_filepath=filepath_base[0:-12]+"all.csv"
print(m_all_filepath)
m_all.to_csv(m_all_filepath, index=False)

# print(m_mean)