# Read Log File in a Plotly Graph

import pandas as pd
import re
import requests
import plotly.express as px
import datetime

#Get Log File Template from here 'https://github.com/jcchouinard/SEO-Projects/blob/master/access_log_20200602-101559.log'

logs = 'access_log_20200602-101559.log'
log_data = []
columns = ['ip','date','http_request','status_code','count','request_url','user_agent']
regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'

        
with open(logs, 'r') as f:
# Get components from each line of the log file into a structured dict
    for line in f:
        line = re.match(regex, line).groups()
        log_data.append(line)
        
log_data = pd.DataFrame(log_data, columns=columns)
log_data['date']= pd.to_datetime(log_data['date'], format='%d/%b/%Y:%H:%M:%S %z')
log_data['date'] =  pd.to_datetime(log_data['date'].dt.strftime('%Y-%m-%d'))

fig = px.line(log_data, x='date', y='count', title='Total Count', color='status_code')
fig.show()