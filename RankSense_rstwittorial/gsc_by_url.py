# Standard library imports
import pandas as pd

# Third party modules imports
from collections import defaultdict
import datetime
from dateutil import relativedelta

# Local modules imports
from date_manip import date_to_str
from oauth import authorize_creds, execute_request

today = datetime.date.today()
days = relativedelta.relativedelta(days=3)
default_end = today - days 

def gsc_by_url(list_of_urls,creds,start_date,end_date=default_end,storage='authorizedcreds.dat'):
    webmasters_service = authorize_creds(creds)     # Get credentials to log in the api
    scDict = defaultdict(list)
    for url in list_of_urls:
        request = {
                    'startDate': date_to_str(start_date),
                    'endDate': date_to_str(end_date),
                    'dimensions': 'page',  #country, device, page, query, searchAppearance
                    'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'page',              
                        'operator': 'equals',           #contains, equals, notEquals, notContains
                        'expression': url
                    }]
                    }]
            }

        response = execute_request(webmasters_service, site, request)
    
        scDict['page'].append(url)

        try:
            for row in response['rows']:
                scDict['clicks'].append(row['clicks'] or 0)
                scDict['impressions'].append(row['impressions'] or 0)
        except Exception as e:
            print(f'An error occurred while extracting {url}: {e}')
    # Add response to dataframe 
    df = pd.DataFrame(data = scDict)
    return df