import argparse
import httplib2
import requests

from collections import defaultdict
from dateutil import relativedelta
from googleapiclient.discovery import build
#from oauth2client.client import OAuth2WebServerFlow
from oauth2client import client
from oauth2client import file
from oauth2client import tools

def authorize_creds(creds, storage='authorizedcreds.dat'):
    print('Authorizing creds')
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
    storage = file.Storage(storage)
    credentials = storage.get()

    # If authenticated credentials don't exist, open Browser to authenticate
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, 'authorizedcreds.dat', flags)
    http = credentials.authorize(http=httplib2.Http())
    webmasters_service = build('webmasters', 'v3', http=http)
    print('Successful authorization')
    return webmasters_service

# Create Function to execute your API Request
def execute_request(service, property_uri, request):
    return service.searchanalytics().query(siteUrl=property_uri, body=request).execute()

