import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import os

# pd.set_option('mode.chained_assignment', 'raise')
pd.set_option('mode.chained_assignment', None)

#region Input parameters
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Custom_dir="E://U87dyeassays_Analysis"

row_B_drug_name='Control'
row_C_drug_name='Pantoprazole_100uM'
row_D_drug_name='NS1643_50uM'
row_E_drug_name='Pantoprazole_100uM_NS1643_50uM'
row_F_drug_name='Retigabine_10uM'
row_G_drug_name='Pantoprazole_100uM_Retigabine_10uM'

#endregion

root = tk.Tk()
root.withdraw()

input_dir_base = filedialog.askdirectory(initialdir=Custom_dir,
# input_dir_base = filedialog.askdirectory(initialdir=BASE_DIR,
                title="Select DiBAC Results Directory")
dir_list = os.listdir(input_dir_base)

# dir_list=[Current_dir]


start_time = time.time()

for input_dir in dir_list:

    print('processing ', input_dir)
    print('--------------------')

    sub_dir= input_dir_base + '/' + input_dir + '/'# you can just write this as << save_dir = input_dir_base  >> if you want to save it in the same base directory as the input files, otherweise specify other directory

    input_fname_GFP="/MyExpt_EditedObjects.csv" # needs "/" in front

    df=pd.read_csv(sub_dir+input_fname_GFP)


    image_n=df.ImageNumber.tolist()# total number of wells
    image_n = list(dict.fromkeys(image_n))


    df['row_id'] =  '_' + df['ImageNumber'].apply(str) + 'and' + df['ObjectNumber'].apply(str) + '_'

    mi=df[['ImageNumber','ObjectNumber','Intensity_MeanIntensity_GFP']]
    mi=mi.rename(columns={"Intensity_MeanIntensity_GFP": "GFP_mean_I"})

    mi['Cell_Num']=mi.groupby(by='ImageNumber')['ImageNumber'].transform('count')

    mi['Row']=''
    mi.Row.loc[(mi.ImageNumber>0)&(mi.ImageNumber<28)]='B'
    mi.Row.loc[(mi.ImageNumber>27)&(mi.ImageNumber<55)]='C'
    mi.Row.loc[(mi.ImageNumber>54)&(mi.ImageNumber<82)]='D'
    mi.Row.loc[(mi.ImageNumber>81)&(mi.ImageNumber<109)]='E'
    mi.Row.loc[(mi.ImageNumber>108)&(mi.ImageNumber<136)]='F'
    mi.Row.loc[(mi.ImageNumber>135)&(mi.ImageNumber<163)]='G'


    mi['Column'] = mi['ImageNumber'].astype(int)
    mi['Column'] = (mi['Column']-1)/9
    mi['Column'] = mi['Column']%3+2
    mi['Column'] = mi['Column'].astype(int)

    mi['Frame'] = mi['ImageNumber'].astype(int)
    # mi['Frame'] = (mi['Frame']-1)
    mi['Frame'] = (mi['Frame']-1)%9+1
    mi['Frame'] = mi['Frame'].astype(int)


    mi['Drug_Name']=mi['Row'].copy()
    mi['Drug_Name'].loc[mi.Drug_Name=='B']=row_B_drug_name
    mi['Drug_Name'].loc[mi.Drug_Name=='C']=row_C_drug_name
    mi['Drug_Name'].loc[mi.Drug_Name=='D']=row_D_drug_name
    mi['Drug_Name'].loc[mi.Drug_Name=='E']=row_E_drug_name
    mi['Drug_Name'].loc[mi.Drug_Name=='F']=row_F_drug_name
    mi['Drug_Name'].loc[mi.Drug_Name=='G']=row_G_drug_name

    mi['Cell_Num'] = mi['Cell_Num'].astype(float)


    means_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).mean()
    stds_frame=mi.groupby(['Row', 'Column', 'Frame','Drug_Name'], as_index=False).std()

    means_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).mean()
    stds_columns=means_frame.groupby(['Row', 'Column','Drug_Name'], as_index=False).std()

    means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
    stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()

    means_rows_control=means_rows.loc[means_rows.Drug_Name=='Control']

    means_columns['Fold_change_GFP_mean_I']=means_columns['GFP_mean_I'].copy()/float(means_rows_control['GFP_mean_I'])

    means_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).mean()
    stds_rows=means_columns.groupby(['Row','Drug_Name'], as_index=False).std()

    mi.to_csv(path_or_buf=sub_dir +input_dir + '_DiBAC.csv',  index=None, header=True)

    means_frame.to_csv(path_or_buf=sub_dir + input_dir + '_DiBACResults_Frame_means.csv',  index=None, header=True)
    means_columns.to_csv(path_or_buf=sub_dir + input_dir + '_DiBACResults_Column_means.csv',  index=None, header=True)
    means_rows.to_csv(path_or_buf=sub_dir + input_dir + '_DiBACResults_Row_means.csv',  index=None, header=True)

    stds_frame.to_csv(path_or_buf=sub_dir + input_dir + '_DiBACResults_Frame_stds.csv',  index=None, header=True)
    stds_columns.to_csv(path_or_buf=sub_dir + input_dir + '_DiBACResults_Column_stds.csv',  index=None, header=True)
    stds_rows.to_csv(path_or_buf=sub_dir + input_dir + '_DiBACResults_Row_stds.csv',  index=None, header=True)

print("\n time spent in seconds: %s" % round(((time.time() - start_time)), 1))