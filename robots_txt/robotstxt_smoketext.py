#!/usr/bin/env python
from datetime import datetime
import json
import os
import requests

from urllib.parse import urlparse

site = 'https://www.jcchouinard.com/'

def main(credentials,site,filename='robots.txt'):
    '''
    Combine all functions
    '''
    url = site + filename
    domain = get_domain_name(site)
    output = path + '/output/' + domain + '/'
    create_project(output)
    r = fetch_page(url)
    output_files = get_robots_files(output)
    compare_robots(credentials,output,output_files,r)

def get_credentials(credentials):
    '''
    Read credentials from JSON file.
    '''
    with open(credentials, 'r') as f:
        creds = json.load(f)
    return creds['slack_webhook']

def post_to_slack(message,credentials):
    '''
    Create header with the message and post to slack.
    '''
    data = {'text':message}
    url = get_credentials(credentials)
    requests.post(url,json=data, verify=False)

def create_project(directory):
    '''
    Create a project if it does not exist
    '''
    if not os.path.exists(directory):
        print('Create project: '+ directory)
        os.makedirs(directory)
    else:
        print(f'{directory} project exists')

def get_domain_name(start_url):
    '''
    Get Domain Name in the www_domain_com format
    1. Parse URL
    2. Get Domain
    3. Replace dots to make a usable folder path
    '''
    url = urlparse(start_url)               # Parse URL into components
    domain_name = url.netloc                # Get Domain (or network location)
    domain_name = domain_name.replace('.','_')# Replace . by _ to create usable folder
    domain_name = domain_name.split(':')[0]
    return domain_name

def get_date():
    '''
    Get today's date as YYYY-MM-DD
    '''
    return datetime.today().strftime('%Y-%m-%d:%H:%M%S')

def fetch_page(url):
    '''
    Use requests to fetch URL
    '''
    try:
        r = requests.get(url)
    except Exception as e:
        print(e)
    return r

def get_robots_files(directory):
    '''
    List robots.txt file in output folder
    '''
    output_files = os.listdir(directory)
    output_files.sort()
    return output_files

def get_robotstxt_name(output_files):
    '''
    Get last saved robots.txt file.
    '''
    robots_txt = 'robots.txt'
    files = []
    for filename in output_files:
        if robots_txt in filename:
            files.append(filename)
    return files[-1]

def read_robotstxt(filename):
    '''
    Read robots.txt
    '''
    if os.path.isfile(filename):
        with open(filename,'r') as f:
            txt = f.read()
    return txt

def write_robotstxt(file, output, filename='robots.txt'):
    '''
    Write robots.txt to file using date as identifier.
    '''
    filename = get_date() + '-' + filename
    filename = output + filename
    print(f'filename: {filename}')
    with open(filename,'w') as f:
        f.write(file)

def compare_robots(credentials,output,output_files,r):
    '''
    Compare previous robots to actual robots.
    If different. Save File.
    '''
    new_robotstxt = r.text.replace('\r', '')
    if output_files:
        robots_filename = get_robotstxt_name(output_files) 
        filename = output + robots_filename
        last_robotstxt = read_robotstxt(filename)
        last_robotstxt = last_robotstxt.replace('\r', '')
        if new_robotstxt != last_robotstxt:
            print('Robots.txt was modified')
            write_robotstxt(new_robotstxt, output)
            message = f'The Robots.txt was changed for {filename}'
            post_to_slack(message,credentials)
        else:
            print('No Change to Robots.txt')
    else:
        print('No Existing Robots.txt. Saving one.')
        write_robotstxt(r.text, output)

if __name__ == '__main__':
    path = os.getcwd()
    credentials = path + '/creds.json'
    main(credentials,site)
