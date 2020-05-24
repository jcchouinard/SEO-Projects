import pandas as pd
import datetime
from datetime import date, timedelta
import httplib2
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from collections import defaultdict
from dateutil import relativedelta
import argparse
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import re
import os
from urllib.parse import urlparse

site = 'https://au.jora.com'    # Property to extract
num_days = 8                    # Number of Days, Months to Extract
creds = 'client_secrets.json'   # Credential file from GSC
output = 'gsc_data.csv'

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
    CLIENT_SECRETS_PATH = creds

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
    storage = file.Storage('authorizedcreds.dat')
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

# Create function to write to CSV
def write_to_csv(data,filename):
    if not os.path.isfile(filename):
        data.to_csv(filename)
    else: # else it exists so append without writing the header
        data.to_csv(filename, mode='a', header=False)

# Read CSV if it exists to find dates that have already been processed.
def get_dates_from_csv(path):
    if os.path.isfile(path):
        data = pd.read_csv(path)
        data = pd.Series(data['date'].unique())
        return data
    else:
        pass

def dt_to_str(date):
    return datetime.datetime.strftime(date,'%Y-%m-%d')

# Create function to extract all the data
def extract_data(site,creds,num_days,output):
    domain_name = get_domain_name(site)             # Get Domain From URL
    create_project(domain_name)                     # Create a new project folder
    full_path = domain_name + '/' + output          # Get Path to add all files
    csv_dt = get_dates_from_csv(full_path)          # Read existing CSV
    webmasters_service = authorize_creds(creds)     # Get credentials to log in the api

    # Set up Dates
    end_date = datetime.date.today() -\
         relativedelta.relativedelta(days=3)        # Start 3 days in the past, since GSC don't show latest data.
    start_date = end_date -\
         relativedelta.relativedelta(days=num_days) # Get end date minus the number of days to go back in time.
    delta = datetime.timedelta(days=1)              # This will let us loop one day at the time
    scDict = defaultdict(list)                      # initialize empty Dict to store data

    while start_date <= end_date:                   # Loop through all dates until start_date is equal to end_date.
        
        # If a GSC csv file exists from previous extraction
        # and dates in the file match to dates we are extracting...
        if csv_dt is not None and \
            csv_dt.str.contains(dt_to_str(start_date)).any(): 
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
                    'startDate': dt_to_str(start_date),     # Get today's date (while loop)
                    'endDate': dt_to_str(start_date),       # Get today's date (while loop)
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
            write_to_csv(df,full_path)                  # Write today's data to CSV file.
        df = pd.read_csv(full_path)
    return df

df = extract_data(site,creds,num_days,output)
df.sort_values('clicks',ascending=False)