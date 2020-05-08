import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from reppy import Robots
from fake_useragent import UserAgent
import json

ua = UserAgent()

url = 'https://ca.indeed.com/Python-jobs'
bad_url = 'https://ca.indeed.com/jobs?q=Python&from=brws&nc=brws'

def get_bot_loc(url):
    domain_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
    bot_loc = domain_url + '/robots.txt'
    return bot_loc

def robot_parser(url):
    bot_loc = get_bot_loc(url)
    parser = Robots.fetch(bot_loc)
    validation = parser.allowed(url, '*')
    return validation


def fetch(url):
    ua = UserAgent()
    header = {'User-Agent':str(ua.random)}
    validation = robot_parser(url)
    if validation:
        try:
            response = requests.get(url, headers=header)
        except requests.exceptions.ConnectionError:
            print('Error: "%s" is not available!' % url)
        content = BeautifulSoup(response.text, 'html.parser') 
    else:
        content = '%s is blocked by robots.txt' % url
        response = 'Blocked'
    return content, response

def write_to_file(data):
    with open('data.json', 'w') as json_file:
        json.dump(data,json_file,indent=2)

def parse(url):
    r = fetch(url)
    response = r[0]
    status_code = r[1].status_code

    if status_code == 200:
        if isinstance(response, BeautifulSoup): # If fetch returns HTML 
            h1, h2, description, title, canonical, hreflang, robot_tag = ([] for i in range(7))

            for h in response.find_all('h1'):
                h1.append(h.text)
            for h in response.find_all('h2'):
                h2.append(h.text)
            for tag in response.find_all('meta', {'name': 'description'}):
                description.append(tag['content'])
            for tag in response.find_all('title'):
                title.append(tag.text)
            for tag in response.find_all('link', {'rel': 'canonical'}):
                canonical.append(tag['href'])
            for tag in response.find_all('link', {'rel': 'alternate'}):
                hreflang.append(tag['href'])
            for tag in response.find_all('meta', {'name': 'robots'}):
                robot_tag.append(tag['content'])
            
            data = {
                'url': url,
                'h1': h1, 
                'h2': h2,
                'description': description,
                'title': title,
                'canonical': canonical,
                'hreflang': hreflang,
                'robot_tag': robot_tag 
            }
            print(data)

            write_to_file(data)
        else:
            print('Could not fetch %s' % url)
    else:
        print('Could not fetch %s, Status code:' % url + str(response.status_code))

parse(url)




