import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir=r"E:\YAP_Perinuc_analysis_set2_center"

# root = tk.Tk()
# root.withdraw()
#
# base_directory = filedialog.askdirectory(initialdir=Custom_dir,
#                 title="Select directory with csv files",)
base_directory=Custom_dir

df_PerinuclearRing = pd.read_csv(base_directory+'\\PerinuclearRing.csv')
df_PerinuclearRing=df_PerinuclearRing[['ImageNumber','ObjectNumber','FileName_Nuclei','Intensity_MeanIntensity_YAP']]

df_Nuclei= pd.read_csv(base_directory+'\\Nuclei.csv')
df_Nuclei=df_Nuclei[['ImageNumber','ObjectNumber','FileName_Nuclei','Intensity_MeanIntensity_YAP']]

df_PerinuclearRing=df_PerinuclearRing.dropna(subset=["Intensity_MeanIntensity_YAP"])
df_PerinuclearRing=df_PerinuclearRing[df_PerinuclearRing.Intensity_MeanIntensity_YAP!=0]
df_PerinuclearRing.reset_index(inplace=True)

print('post processing length PerinuclearRing', len(df_PerinuclearRing))


PerinuclearRing_FileNames_ObjectID=(df_PerinuclearRing['FileName_Nuclei'] + '_and_' + df_PerinuclearRing['ObjectNumber'].apply(str)).tolist()

df_Nuclei['FileNames_Object_number_Nuclei']=(df_Nuclei['FileName_Nuclei'] + '_and_' + df_Nuclei['ObjectNumber'].apply(str)).tolist()

print('pre processing length Nuclei', len(df_Nuclei))
df_Nuclei=df_Nuclei[df_Nuclei['FileNames_Object_number_Nuclei'].isin(PerinuclearRing_FileNames_ObjectID)]
print('post processing length Nuclei', len(df_Nuclei))
df_Nuclei.reset_index(inplace=True)

df_Nuclei.drop(columns=['FileNames_Object_number_Nuclei'],inplace=True)


print(df_PerinuclearRing.dtypes)

df_Nuclei.to_csv(base_directory + '\\Nuclei_from_Perinuclear.csv')

df_Nuclei_norm_to_Perinuclear=df_Nuclei.copy()
df_Nuclei_norm_to_Perinuclear.Intensity_MeanIntensity_YAP= df_Nuclei_norm_to_Perinuclear.Intensity_MeanIntensity_YAP/df_PerinuclearRing.Intensity_MeanIntensity_YAP
df_Nuclei_norm_to_Perinuclear['Math_NucByRingYAP']=np.log10(df_Nuclei_norm_to_Perinuclear.Intensity_MeanIntensity_YAP)

df_Nuclei_norm_to_Perinuclear.to_csv(base_directory + '\\Nuclei_from_Perinuclear_normalized.csv')