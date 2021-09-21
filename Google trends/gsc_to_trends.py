from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd 

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pytrends.request import TrendReq
import searchconsole


property_url = 'https://www.jcchouinard.com/'
geo = ''
# max 5 topics
# https://medium.com/analytics-vidhya/compare-more-than-5-keywords-in-google-trends-search-using-pytrends-3462d6b5ad62
topics = ['python seo']#['/m/019qb_']#

def authenticate(secret='client_secrets.json', token='credentials.json'):
    if os.path.isfile('credentials.json'):
        account = searchconsole.authenticate(client_config=secret,
                                            credentials=token)
    else:
        account = searchconsole.authenticate(client_config=secret,
                                        serialize=token)
    return account


def extract_gsc(property_url):
    print(f'Extracting GSC data: {property_url}')
    webproperty = account[property_url]
    report = webproperty.query\
            .range('today', months=-16)\
            .dimension('date')\
            .get()
    return report.to_dataframe()


def daily_to_weekly(df):
    # bring daily data to weekly format
    print('Converting dates to weekly format')
    df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
    df = df.groupby(pd.Grouper(key='date', freq='W-SUN'))['clicks','impressions'].sum()
    df = df.reset_index().sort_values('date')
    return df


def extract_google_trend(**kwargs):
    # Only need to run this once, 
    # other requests will use the same session.
    print('Extracting Google Trends data')
    pytrend = TrendReq()
    pytrend.build_payload(**kwargs)
    trend_data = pytrend.interest_over_time()
    trend_data['interest'] = trend_data[topics].sum(axis=1)
    return trend_data.reset_index()


def combine_gsc_to_gtrends(gsc_df, gtrends_df):
    # combine GSC data to google trend 
    print('Combining GSC data to Trends')
    g = pd.merge(gsc_df, gtrends_df, on='date')
    g.drop(g.tail(1).index, inplace=True)
    return g


def compute_seasonality(df, col):
    print('Computing seasonality')
    df['seasonnality_index'] = df[col] / df[col].mean()
    df['WoW_perc'] = df['seasonnality_index'].pct_change()
    df['WoW_perc'] = df['WoW_perc'].fillna(0)
    return df



account = authenticate()

df = extract_gsc(property_url)
df = daily_to_weekly(df)

end_date = datetime.today()
start_date = end_date - relativedelta(months=16) 
end_date = end_date.strftime('%Y-%m-%d')
start_date = start_date.strftime('%Y-%m-%d')
timeframe = f'{start_date} {end_date}'
if not geo: 
    trend_data = extract_google_trend(
        kw_list = topics,
        timeframe = timeframe
        )
else:
    trend_data = extract_google_trend(
        kw_list = topics,
        geo = geo,
        timeframe = timeframe
        )

g = combine_gsc_to_gtrends(df, trend_data)

g = compute_seasonality(g, 'interest')

# dropping first and las row as they are often and incomplete week
# g = g.drop(0).reset_index(drop=True)
# g.drop(g.tail(1).index,inplace=True)
# make prediction
g['prediction'] = g['clicks']
for i in range(len(g)):
    if i == 0:
        g.loc[i,'prediction'] = g.loc[i,'clicks']
    else:
        prev_clicks = g.loc[i-1,'prediction'] 
        perc_variation = g.loc[i,'seasonnality_index']
        pred = prev_clicks * perc_variation
        # print(i, g.loc[i,'date'], g.loc[i,'clicks'], g.loc[i,'interest'])
        # print(prev_clicks, perc_variation, pred) 
        g.loc[i,'prediction'] = pred

# plot the graph
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(
        x=g['date'], 
        y=g['prediction'], 
        name='Prediction'
        ),
        secondary_y=False
    )
fig.add_trace(
    go.Scatter(
        x=g['date'],
        y=g['clicks'],
        name='Clicks'),
    secondary_y=False
    )
fig.add_trace(
    go.Scatter(
        x=g['date'],
        y=g['interest'],
        name='Trend'),
    secondary_y=True
    )
fig.update_layout(title_text=f'Clicks Vs Prediction - {property_url}')
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text="<b>Traffic:</b> Pred VS Actual", secondary_y=False)
fig.update_yaxes(title_text="<b>Google Trends</b> data", secondary_y=True)

fig.show()
