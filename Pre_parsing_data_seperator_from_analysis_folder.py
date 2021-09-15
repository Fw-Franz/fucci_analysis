import numpy as np
import seaborn as sns
import pandas as pd
import time
import os

start_time = time.time()
base_directory =  os.getcwd() + '\\'
input_dir_base = base_directory

#region Input parameters

date='08_07_2021' # sth like '01_21_2021'

input_fname_GFAP="GFAP.csv"
input_fname_nuclei="Nuclei.csv"

fname_strings=['MAP2_byloc_Plate','NFKb_BS_Plate','cmyc_BS_Plate']

#endregion

save_dir_base=input_dir_base + date+ '//'

CHECK_FOLDER = os.path.isdir(save_dir_base)
# If folder doesn't exist, then create it.
if not CHECK_FOLDER:
    os.mkdir(save_dir_base)

print('loading data ... ')

df_GFAP=pd.read_csv(input_dir_base+input_fname_GFAP)
df_nuclei=pd.read_csv(input_dir_base+input_fname_nuclei)

def search_and_save(df_GFAP,df_nuclei,save_dir_base,fname_string):

    save_dir_i=save_dir_base+fname_string+'//'

    CHECK_FOLDER = os.path.isdir(save_dir_i)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.mkdir(save_dir_i)

    df_GFAP_i= df_GFAP.loc[df_GFAP['FileName_DisplayImage'].str.contains(fname_string, case=False)]
    df_nuclei_i= df_nuclei.loc[df_nuclei['FileName_DisplayImage'].str.contains(fname_string, case=False)]

    df_GFAP_i.to_csv(path_or_buf=save_dir_i + 'GFAP.csv',  index=None, header=True)
    df_nuclei_i.to_csv(path_or_buf=save_dir_i + 'Nuclei.csv',  index=None, header=True)

for fname_string in fname_strings:
    search_and_save(df_GFAP,df_nuclei,save_dir_base,fname_string)

print("\n time spent in minutes: %s" % round(((time.time() - start_time))/60, 1))