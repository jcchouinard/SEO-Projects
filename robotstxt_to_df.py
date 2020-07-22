import pandas as pd
import os
from urllib.parse import urlparse

ua = 'User-agent'

def get_robots_url(url):
    domain_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
    robots_url = domain_url + '/robots.txt'
    return robots_url

def read_robots_txt(url):
    robot_url = get_robots_url(url)
    robot_file = os.popen(f'curl {robot_url}').read()
    return robot_file


def initialize_dict(url):
    robot_file = read_robots_txt(url)
    result_data_set = {ua:{}}
    for line in robot_file.split("\n"):
        if line.startswith(ua):
            result_data_set[ua].update({line.split(':')[1].strip():{}})
    keys = []
    for key in result_data_set[ua].keys():
        keys.append(key)
    return result_data_set, keys, robot_file

def parse_robot(url):
    idict = initialize_dict(url)
    result_data_set = idict[0]
    keys = idict[1]
    robot_file = idict[2]
    print_flag = False
    for i in range(len(keys)):
        if i <= len(keys)-2:
            end_str = keys[i+1]
        else:
            end_str = 'We are done'

        result_data_set[ua][keys[i]]['Disallow'] = []
        result_data_set[ua][keys[i]]['Allow'] = []
        for line in robot_file.split("\n"):
            if end_str in line:
                print_flag = False
            elif keys[i] in line:
                print_flag = True
            elif print_flag:
                if line.startswith('Disallow') or line.startswith('Allow'):
                    status = line.split(':')[0].strip()
                    val = line.split(':')[1].strip()
                    result_data_set[ua][keys[i]][status].append(val)
    return result_data_set

def robots_to_df(url):
    result_data_set = parse_robot(url)
    ls = {ua:[],'Status':[],'Pattern':[]}
    for k,v in result_data_set.items():
        for v in result_data_set[k]:
            for key,value in result_data_set[k][v].items():
                for value in result_data_set[k][v][key]:
                    ls[ua].append(v)
                    ls['Status'].append(key)
                    ls['Pattern'].append(value)
    robots_df = pd.DataFrame.from_dict(ls)
    return robots_df


robots_to_df(url)