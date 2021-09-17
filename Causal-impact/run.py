# Based on this blog post: https://www.jcchouinard.com/pycausalimpact/
import os
import searchconsole

from causal import Causal

# define metric that you want to test
# impressions, clicks, ctr
metric = 'clicks' 

# define intervention data
intervention = '2021-08-01'

# give the path of your credential file
client_secrets = 'client_secrets.json'

# define sites on which you ran the experiment (required)
test_sites = [
    'https://ca.example.com/', 
    'https://us.example.com/', 
    'https://au.example.com/'
    ]

# define control sites that were not shown the experiment (optional)
# set list as empty [] to run simple pre-post experiment
control_sites = [
    'https://www.example.fr/',
    'https://uk.example.com/'
    ]


def authenticate(config='client_secrets.json', token='credentials.json'):
    """Authenticate GSC"""
    if os.path.isfile(token):
        account = searchconsole.authenticate(client_config=config,
                                            credentials=token)
    else:
        account = searchconsole.authenticate(client_config=config,
                                        serialize=token)
    return account


if __name__ == '__main__':
    account = authenticate(config=client_secrets)
    c = Causal(
        account,
        intervention,
        test_sites,
        control_sites=control_sites, 
        metric='clicks')
    c.run_causal()