import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import os

# region pick repeats
repeats=['biological','technical']   # enter ['biological','technical'] or delete one of them
# end region


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="E:\\U87_Combo_YAP_analysissheets\\U87_Center_YAP_set1"

# root = tk.Tk()
# root.withdraw()
#
# base_directory = filedialog.askdirectory(initialdir=Custom_dir,
#                 title="Select directory with csv files",)
base_directory=Custom_dir

df_EditedObjects = pd.read_csv(base_directory+'\\EditedObjects.csv')
df_GFAP = pd.read_csv(base_directory+'\\GFAP.csv')
df_Cytoplasm = pd.read_csv(base_directory+'\\Cytoplasm.csv')
df_FilteredNuclei= pd.read_csv(base_directory+'\\FilteredNuclei.csv')

EditedObjects_FileNames_Parent_GFAP=(df_EditedObjects['FileName_DisplayImage'] + '_and_' + df_EditedObjects['Parent_GFAP'].apply(str)).tolist()

df_GFAP['FileNames_Parent_GFAP']=(df_GFAP['FileName_DisplayImage'] + '_and_' + df_GFAP['ObjectNumber'].apply(str)).tolist()
print('pre processing length GFAP', len(df_GFAP))
df_GFAP=df_GFAP[df_GFAP['FileNames_Parent_GFAP'].isin(EditedObjects_FileNames_Parent_GFAP)]
print('post processing length GFAP', len(df_GFAP))

GFAP_FileNames_Parent_Nuclei=(df_GFAP['FileName_DisplayImage'] + '_and_' + df_GFAP['Parent_Nuclei'].apply(str)).tolist()
Cytoplasm_FileNames_Parent_Nuclei=(df_Cytoplasm['FileName_DisplayImage'] + '_and_' + df_Cytoplasm['Parent_FilteredNuclei'].apply(str)).tolist()

df_FilteredNuclei_EditedObjects=df_FilteredNuclei.copy()
df_FilteredNuclei_EditedObjects['FileNames_Parent_Nuclei']=(df_FilteredNuclei_EditedObjects['FileName_DisplayImage'] + '_and_' + df_FilteredNuclei_EditedObjects['ObjectNumber'].apply(str)).tolist()
print('pre processing length FilteredNuclei', len(df_FilteredNuclei_EditedObjects))
df_FilteredNuclei_EditedObjects=df_FilteredNuclei_EditedObjects[df_FilteredNuclei_EditedObjects['FileNames_Parent_Nuclei'].isin(GFAP_FileNames_Parent_Nuclei)]
print('post processing length FilteredNuclei', len(df_FilteredNuclei_EditedObjects))

df_FilteredNuclei_Cytoplasm=df_FilteredNuclei.copy()
df_FilteredNuclei_Cytoplasm['FileNames_Parent_Nuclei']=(df_FilteredNuclei_Cytoplasm['FileName_DisplayImage'] + '_and_' + df_FilteredNuclei_Cytoplasm['ObjectNumber'].apply(str)).tolist()
print('pre processing length FilteredNuclei', len(df_FilteredNuclei_Cytoplasm))
df_FilteredNuclei_Cytoplasm=df_FilteredNuclei_Cytoplasm[df_FilteredNuclei_Cytoplasm['FileNames_Parent_Nuclei'].isin(Cytoplasm_FileNames_Parent_Nuclei)]
print('post processing length FilteredNuclei', len(df_FilteredNuclei_Cytoplasm))

df_FilteredNuclei_EditedObjects.to_csv(base_directory + '\\FilteredNuclei_from_EditedObjects.csv')
df_FilteredNuclei_Cytoplasm.to_csv(base_directory + '\\FilteredNuclei_from_Cytoplasm.csv')

df_FilteredNuclei_Cytoplasm.reset_index(inplace=True)
df_Cytoplasm.reset_index(inplace=True)

df_FilteredNuclei_by_Cytoplasm_normalized=df_FilteredNuclei_Cytoplasm.copy()
df_FilteredNuclei_by_Cytoplasm_normalized['Intensity_MeanIntensity_OrigGreen']=\
    df_FilteredNuclei_Cytoplasm['Intensity_MeanIntensity_OrigGreen']/df_Cytoplasm['Intensity_MeanIntensity_OrigGreen']

df_FilteredNuclei_by_Cytoplasm_normalized['Intensity_IntegratedIntensity_OrigGreen']=\
    df_FilteredNuclei_Cytoplasm['Intensity_IntegratedIntensity_OrigGreen']/df_Cytoplasm['Intensity_IntegratedIntensity_OrigGreen']

df_FilteredNuclei_by_Cytoplasm_normalized.to_csv(base_directory + '\\FilteredNuclei_from_Cytoplasm_by_Cytoplasm_normalized.csv')

df_Cytoplasm_by_FilteredNuclei_normalized=df_FilteredNuclei_Cytoplasm.copy()
df_Cytoplasm_by_FilteredNuclei_normalized['Intensity_MeanIntensity_OrigGreen']=\
    df_Cytoplasm['Intensity_MeanIntensity_OrigGreen']/df_FilteredNuclei_Cytoplasm['Intensity_MeanIntensity_OrigGreen']

df_Cytoplasm_by_FilteredNuclei_normalized['Intensity_IntegratedIntensity_OrigGreen']=\
    df_Cytoplasm['Intensity_IntegratedIntensity_OrigGreen']/df_FilteredNuclei_Cytoplasm['Intensity_IntegratedIntensity_OrigGreen']

df_Cytoplasm_by_FilteredNuclei_normalized.to_csv(base_directory + '\\Cytoplasm_by_FilteredNuclei_normalized.csv')