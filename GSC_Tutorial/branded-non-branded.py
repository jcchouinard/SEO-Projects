import matplotlib.pyplot as plt
import pandas as pd

import file_manip as fm

site = 'https://www.jcchouinard.com'
filename = 'gsc_data.csv'

df = fm.return_df(site,filename)
r = r'.*chouinard.*'
df['query_type'] = ''
df['query_type'][df['query'].str.contains(r,regex=True)] = 'Brand'
df['query_type'][~df['query'].str.contains(r,regex=True)] = 'Non-Brand'

df = fm.return_df(v['url'],filename)
df['query_type'] = ''
df['query_type'][~df['query'].str.contains(v['brand'],regex=True)] = 'Non-Brand'
df['query_type'][df['query'].str.contains(v['brand'],regex=True)] = 'Brand'
t = df.groupby(['date','query_type'])['clicks'].sum().reset_index()
t = t.set_index(['date','query_type'])['clicks'].unstack()
t = t.reset_index().rename_axis(None, axis=1)
t = fm.date_to_index(t,'date')
t.plot(subplots=True,
        sharex=True,
        figsize=(6,6),
        sharey=False)
plt.show()