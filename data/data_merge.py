# %%
import datetime as dt
import os
from zipfile import ZipFile

import pandas as pd
from genericpath import isdir
from tqdm import tqdm

dir_path = os.path.dirname(os.path.realpath(__file__))

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)

# %% Check if unzipped zipfile
if not isdir(dir_path+'/archive-stations-limoilair/'):
    with ZipFile('archive-stations-limoilair.zip', 'r') as zipAir:
        zipAir.extractall()

# %% List of directories
start_date = dt.date(2022,5,1)
end_date = dt.date(2022,9,5)

data_date_list = [x.strftime("%Y-%m-%d") for x in daterange(start_date, end_date)]
data_dir_list = [dir_path+'/archive-stations-limoilair/'+d+'/' for d in data_date_list]

# %% Load data per dir 

# Load all index files for lat-lon and features of sensors
df_index_list = [pd.read_csv(dir+"index.csv") for dir in data_dir_list]
df_indexes = pd.concat(df_index_list).drop_duplicates().reset_index(drop=True)
# Spaces seems left on columns names ...
df_indexes.rename(columns=lambda x: x.strip(), inplace=True)

# Load all datafiles in all directory
df_dir_cat = []
for dir in tqdm(data_dir_list): 
    data_file_list = [f for f in os.listdir(dir) 
                    if os.path.isfile(dir+f) and str.startswith(f,'20')]
    
    # Load all files in the diectory
    df_file_cat = []
    for file in tqdm(data_file_list, leave=False):
        df_file = pd.read_csv(dir+file, skiprows=1)
        
        # Error in some CSV where no license row : 
        if not 'Date (UTC)' in df_file.columns:
            df_file = pd.read_csv(dir+file)
            
        df_file['Date'] = file[0:10] #df_file['Date (UTC)'].apply(lambda x:dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S').date())
        df_file['Slug'] = file[11:-4]
        # add sensor features to datapoint
        df_file = pd.merge(df_file, df_indexes, on='Slug', how='inner')
        df_file_cat.append(df_file)
    # Concat all files in the directory
    df_files = pd.concat(df_file_cat).drop_duplicates().reset_index(drop=True)
    df_dir_cat.append(df_files)

# %% Save all sensors per day
if not isdir(dir_path+'/par_date/'):
    os.mkdir('par_date')
for df in tqdm(df_dir_cat):
    df.to_csv(dir_path+'/par_date/'+df['Date'].iloc[0]+'.csv')

# %% Concat all dates in same file
# WAY too much memory for my laptop :)
df_all = pd.concat(df_dir_cat).drop_duplicates().reset_index(drop=True)
df_all.to_csv(dir_path+'/all.csv')

# %%
