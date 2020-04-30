"""
This Script will backup your Google Search Console Data automatically in a MySQL database using Python.

@author: Jean-Christophe Chouinard: Technical SEO / Data Scientist. 
Twitter > https://www.twitter.com/ChouinardJC, 
LinkedIn > https://www.linkedin.com/in/jeanchristophechouinard/, 
Blog > https://www.jcchouinard.com/

"""

import pandas as pd
import datetime
import httplib2
from apiclient.discovery import build
from collections import defaultdict
from dateutil import relativedelta
import argparse
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import pymysql.cursors
import sqlalchemy

"""
Step 1: Create your db (the first time only)
connection = pymysql.connect(host='localhost',
                             user='root',
                             port='',
                             password='')

# Simulate the CREATE DATABASE function of mySQL
try:
    with connection.cursor() as cursor:
        cursor.execute('CREATE DATABASE gsc_db')

finally:
    connection.close()



Step 2: Create your table and/or connect to it
"""
connection = pymysql.connect(host='localhost',
                             user='root',
                             port='',
                             password='',
                             db='gsc_db',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        sqlQuery = '''CREATE TABLE IF NOT EXISTS backup_gsc(Date DATE, 
                                                            Page LONGTEXT, 
                                                            Query LONGTEXT, 
                                                            Clicks INT, 
                                                            Impressions INT, 
                                                            Ctr DECIMAL(10,2), 
                                                            Position DECIMAL(3,2))'''
        cursor.execute(sqlQuery)
finally:
    connection.close()


"""
Step 3: Connect to the API
"""
site = 'https://www.yoursite.com'

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
DISCOVERY_URI = ('https://www.googleapis.com/discovery/v1/apis/customsearch/v1/rest')

CLIENT_SECRETS_PATH = r'C:\Users\YOUR-PATH\client_secrets.json' # Path to client_secrets.json file.

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])
flags = parser.parse_args([])


flow = client.flow_from_clientsecrets(
    CLIENT_SECRETS_PATH, scope=SCOPES,
    message=tools.message_if_missing(CLIENT_SECRETS_PATH))

storage = file.Storage('searchconsole.dat')
credentials = storage.get()

if credentials is None or credentials.invalid:
  credentials = tools.run_flow(flow, storage, flags)
http = credentials.authorize(http=httplib2.Http())

webmasters_service = build('webmasters', 'v3', http=http)

"""
Step 4: Query All Your Search Traffic
"""
#Set Date
end_date = datetime.date.today()-relativedelta.relativedelta(days=3)
start_date = end_date 

#Execute your API Request
def execute_request(service, property_uri, request):
    return service.searchanalytics().query(siteUrl=property_uri, body=request).execute()

#Get more than 25000 rows
maxRows = 25000; 
i = 0;
numRows = maxRows;
scDict = defaultdict(list);

while (numRows == 25000 and i < 40) : # Limit to 1M rows
    request = {
        'startDate': datetime.datetime.strftime(start_date,"%Y-%m-%d"),
        'endDate': datetime.datetime.strftime(end_date,'%Y-%m-%d'),
        'dimensions': ['date','page','query'],
        'rowLimit': maxRows, 
        'startRow': i*maxRows
    }
    response = execute_request(webmasters_service, site, request)
#Process the response
    for row in response['rows']:
        scDict['date'].append(row['keys'][0] or 0)    
        scDict['page'].append(row['keys'][1] or 0)
        scDict['query'].append(row['keys'][2] or 0)
        scDict['clicks'].append(row['clicks'] or 0)
        scDict['ctr'].append(row['ctr'] or 0)
        scDict['impressions'].append(row['impressions'] or 0)
        scDict['position'].append(row['position'] or 0)

  #Add response to dataframe 
    df = pd.DataFrame(data = scDict)
    df['clicks'] = df['clicks'].astype('int')
    df['ctr'] = df['ctr']*100
    df['impressions'] = df['impressions'].astype('int')
    df['position'] = df['position'].round(2)
    df.sort_values('clicks',inplace=True,ascending=False)
    numRows=len(response['rows'])
    i=i+1


"""
Step 5: Save your data to the MySQL database
"""

engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost/gsc_db')
df.columns
df.to_sql(
        name = 'backup_gsc',
        con = engine,
        index = False,
        if_exists = 'append')
