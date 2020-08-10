import json
import glob
import os
import pandas as pd

from urllib.parse import urlparse

from date_manip import get_dates

# Create a project if it does not exist
def create_project(directory):
    if not os.path.exists(directory):
        print('Create project: '+ directory)
        os.makedirs(directory)
    else:
        print(f'{directory} project exists')

# Get Domain Name to Create a Project
def get_domain_name(start_url):
    domain_name = '{uri.netloc}'.format(uri=urlparse(start_url))  # Get Domain Name To Name Project
    domain_name = domain_name.replace('.','_')
    return domain_name

# Write to a JSON file
def write_to_json(data,filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Write to a CSV file
def write_to_csv(data,filename):
    if not os.path.isfile(filename):
        data.to_csv(filename, index=False)
    else: # else it exists so append without writing the header
        data.to_csv(filename, mode='a', header=False, index=False)

# Convert date column to a datetime Index
def date_to_index(df,datecol):
    if df.index.name == datecol:
        if isinstance(df.index, pd.DatetimeIndex):
            print(f'{datecol} is already a datetime index')
        else:
            df[datecol] = pd.to_datetime(df[datecol])
    else:
        df[datecol] = pd.to_datetime(df[datecol])
        df = df.set_index(datecol)
    return df

# Overwrite CSV without duplicates
def drop_duplicates(filename):
    f = pd.read_csv(filename).drop_duplicates(keep=False)
    f.to_csv(filename)

# Define where to export CSVs
def get_full_path(site,filename,date):
    YM_date = get_dates(date)[0]    # Get date as YYYY-MM
    output_path = YM_date + '_' + filename  # Add file location
    output = os.path.join(output_path)      # Merge to create YYYY-MM_filename.csv
    domain_name = get_domain_name(site)  # Get domain from site URL
    data_path = domain_name + '/' 
    full_path = data_path + output          # Output will be at /your_site_com/YYYY-MM_filename.csv
    return output, domain_name, full_path, data_path

# Check all files that ends with your filename to gather dates from
def loop_csv(full_path,filename):
    file_list = []
    for file in os.listdir(full_path):
        if file.endswith(os.path.join('_'+ filename)):
            file_list.append(file)
            file_list.sort()
    return file_list

# Read CSV if it exists to find dates that have already been processed.
def get_dates_from_csv(path):
    if os.path.isfile(path):
        data = pd.read_csv(path)
        data = pd.Series(data['date'].unique())
        return data
    else:
        pass

# Check All CSVs to check all dates that have been processed
def get_dates_csvs(full_path,site,filename):
    print(f'Checking existing dates in {full_path}')
    dset = set()
    csvs = loop_csv(full_path,filename)
    for csv in csvs:
        path = os.path.join(full_path + csv)
        dates = get_dates_from_csv(path)
        for date in dates:
            dset.add(date)
    return dset

# Read all dataframes in path
def read_all_dfs(path,filename):
    dfs = []
    files =[]
    globs = glob.glob(f'{path}/*{filename}')
    for g in globs:
        files.append(g)
    for f in files:
        print(f)
        df = pd.read_csv(f)
        dfs.append(df)
    full_df = pd.concat(dfs)
    return full_df

# Convert dict to DF
def scdict_to_df(scDict,clicks=True,impressions=True,ctr=False,position=False):
    df = pd.DataFrame(data = scDict)
    if clicks:
        df['clicks'] = df['clicks'].astype('int')
    if impressions:
        df['impressions'] = df['impressions'].astype('int')
    if ctr:
        df['ctr'] = df['ctr']*100
    if position:
        df['position'] = df['position'].round(2)
    df.sort_values('clicks',inplace=True,ascending=False)
    return df

# Read All csvs to a combined dataframe
def return_df(site,filename):
    folder = get_domain_name(site)
    df = read_all_dfs(folder,filename)  
    return df