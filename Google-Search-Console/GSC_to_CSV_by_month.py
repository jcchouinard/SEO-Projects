import pandas as pd
import datetime
from datetime import date, timedelta
from dateutil import relativedelta
import httplib2
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from collections import defaultdict
import argparse
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import re
import os
from urllib.parse import urlparse
import time


site = 'https://www.example.com'    # Property to extract                   # Number of Days, Months to Extract
path = os.getcwd()
creds = 'client_secrets.json'   # Credential file from GSC
filename = 'gsc_data.csv'
man_st_dt = '2020-04-23' # Leave empty to start at beginning of the month

# Get Domain Name to Create a Project
def get_domain_name(start_url):
    domain_name = '{uri.netloc}'.format(uri=urlparse(start_url))  # Get Domain Name To Name Project
    domain_name = domain_name.replace('.','_')
    return domain_name


# Create a project Directory for this website
def create_project(directory):
    if not os.path.exists(directory):
        print('Create project: '+ directory)
        os.makedirs(directory)

def authorize_creds(creds):
    # Variable parameter that controls the set of resources that the access token permits.
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly'] 

    # Path to client_secrets.json file
    CLIENT_SECRETS_PATH = path + '/' + creds

    # Create a parser to be able to open browser for Authorization
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])

    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_PATH, scope = SCOPES,
        message = tools.message_if_missing(CLIENT_SECRETS_PATH))

    # Prepare credentials and authorize HTTP
    # If they exist, get them from the storage object
    # credentials will get written back to a file.
    storage = file.Storage(path + '/authorizedcreds.dat')
    credentials = storage.get()

    # If authenticated credentials don't exist, open Browser to authenticate
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())
    webmasters_service = build('webmasters', 'v3', http=http)
    return webmasters_service

# Create Function to execute your API Request
def execute_request(service, property_uri, request):
    return service.searchanalytics().query(siteUrl=property_uri, body=request).execute()

# Convert dates to strings
def dt_to_str(date):
    full_date = datetime.datetime.strftime(date,'%Y-%m-%d')
    yr_m = datetime.datetime.strftime(date,'%Y-%m')
    return full_date, yr_m

# Get Days since start of month
def get_dates(man_st_dt):
    end_date = datetime.date.today() - relativedelta.relativedelta(days=3)  
    if man_st_dt is '':
        delta = end_date - datetime.date.today().replace(day=1) # Get first day of the month
        start_date = end_date - delta # count difference between end date and first day of the month
    else:
        delta = end_date - datetime.datetime.strptime(man_st_dt,'%Y-%m-%d').date() # Get first day of the month
        start_date = end_date - delta # count difference between end date and first day of the month
    str_date = dt_to_str(start_date)[1]
    return str_date, start_date, end_date

# Create function to write to CSV
def write_to_csv(data,filename):
    if not os.path.isfile(filename):
        data.to_csv(filename, index=False)
    else: # else it exists so append without writing the header
        data.to_csv(filename, mode='a', header=False, index=False)


def get_full_path(site,filename):
    output = os.path.join(get_dates(man_st_dt)[0] + '_' + filename)
    domain_name = get_domain_name(site) 
    data_path = domain_name + '/' 
    full_path = data_path + output  
    return output, domain_name, full_path, data_path

def loop_csv(filename):
    path = get_full_path(site,filename)[3]
    file_list = []
    for file in os.listdir(path):
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


def get_dates_csvs(site,filename):
    full_path = get_full_path(site,filename)[3]
    dset = set()
    csvs = loop_csv(filename)
    for csv in csvs:
        path = os.path.join(full_path + csv)
        dates = get_dates_from_csv(path)
        for date in dates:
            dset.add(date)
    return dset

# Create function to extract all the data
def gsc_to_csv(site,creds,filename):
    domain_name = get_full_path(site,filename)[1]   # Get Domain From URL
    #full_path = get_full_path(site,filename)[2]     # Get Path to add all files
    #print(full_path)
    create_project(domain_name)                     # Create a new project folder
    csv_dt = get_dates_csvs(site,filename)
    #csv_dt = get_dates_from_csv(full_path)          # Read existing CSV
    webmasters_service = authorize_creds(creds)     # Get credentials to log in the api

    # Set up Dates
    start_date = get_dates(man_st_dt)[1]                     # Start first day of the month.
    end_date = get_dates(man_st_dt)[2]                       # End 3 days in the past, since GSC don't show latest data.
    delta = datetime.timedelta(days=1)              # This will let us loop one day at the time
    scDict = defaultdict(list)                      # initialize empty Dict to store data
    while start_date <= end_date:                   # Loop through all dates until start_date is equal to end_date.
        curr_month = dt_to_str(start_date)[1]
        full_path = os.path.join(get_full_path(site,filename)[3] + curr_month + '_' + filename)
        print(full_path)
        # If a GSC csv file exists from previous extraction
        # and dates in the file match to dates we are extracting...
        if csv_dt is not None and \
            dt_to_str(start_date)[0] in csv_dt:
            #csv_dt.str.contains(dt_to_str(start_date)[0]).any(): 
            print('Existing Date: %s' % start_date) #... Print the date
            start_date += delta                     #... and increment without extraction  
        else:                                       # If the file doesn't exist, or date don't match...
            # ... Print and start the extraction
            print('Start date at beginning: %s' % start_date)

            maxRows = 25000 # Maximum 25K per call 
            numRows = 0     # Start at Row Zero
            status = ''     # Initialize status of extraction


            while (status != 'Finished') : # As long as today's data have not been fully extracted.
                # Extract this information from GSC
                request = {
                    'startDate': dt_to_str(start_date)[0],     # Get today's date (while loop)
                    'endDate': dt_to_str(start_date)[0],       # Get today's date (while loop)
                    'dimensions': ['date','page','query'],  # Extract This information
                    'rowLimit': maxRows,                    # Set number of rows to extract at once (max 25k)
                    'startRow': numRows                     # Start at row 0, then row 25k, then row 50k... until with all.
                }

                response = execute_request(webmasters_service, site, request)
                
                #Process the response
                try:
                    for row in response['rows']:
                        scDict['date'].append(row['keys'][0] or 0)    
                        scDict['page'].append(row['keys'][1] or 0)
                        scDict['query'].append(row['keys'][2] or 0)
                        scDict['clicks'].append(row['clicks'] or 0)
                        scDict['ctr'].append(row['ctr'] or 0)
                        scDict['impressions'].append(row['impressions'] or 0)
                        scDict['position'].append(row['position'] or 0)
                    print('successful at %i' % numRows)

                except:
                    print('error occurred at %i' % numRows)

                # Add response to dataframe 
                df = pd.DataFrame(data = scDict)
                df['clicks'] = df['clicks'].astype('int')
                df['ctr'] = df['ctr']*100
                df['impressions'] = df['impressions'].astype('int')
                df['position'] = df['position'].round(2)

                # Increment the 'start_row'
                print('Numrows at the start of loop: %i' % numRows)
                try: 
                    numRows = numRows + len(response['rows'])
                except:
                    status = 'Finished'                 # If no response left, change status
                print('Numrows at the end of loop: %i' % numRows)
                if numRows % maxRows != 0:              # If numRows not divisible by 25k...
                    status = 'Finished'                 # change status, you have covered all lines.                
        
            start_date += delta                         # Increment start_date to continue the loop
            print('Start date at end: %s' % start_date) 
            write_to_csv(df[df['date'].str.contains(curr_month)],full_path)                  # Write today's data to CSV file.
        

def return_df(site,filename):
    full_path = get_full_path(site,filename)[2]
    df = pd.read_csv(full_path)
    df.sort_values('clicks',ascending=False).reset_index(inplace=True)


gsc_to_csv(site,creds,filename)

print('Done')
#return_df(site,filename)

