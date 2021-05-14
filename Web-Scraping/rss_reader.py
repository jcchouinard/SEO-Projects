# Read a RSS Feed with Python and BeautifulSoup
# https://www.jcchouinard.com/read-rss-feed-with-python/

# Author: Jean-Christophe Chouinard
# Role: Sr. SEO Specialist at Seek.com.au
# twitter: twitter.com/ChouinardJC
# linkedin: linkedin.com/in/jeanchristophechouinard

from bs4 import BeautifulSoup
import requests

headers = {
            'User-Agent': 'your-user-agent-here'
        }

class ReadRss:

    def __init__(self, rss_url, headers):

        self.url = rss_url
        self.headers = headers
        try:
            self.r = requests.get(rss_url, headers=self.headers)
            self.status_code = self.r.status_code
        except Exception as e:
            print('Error fetching the URL: ', rss_url)
            print(e)
        try:    
            self.soup = BeautifulSoup(self.r.text, 'lxml')
        except Exception as e:
            print('Could not parse the xml: ', self.url)
            print(e)
        self.articles = self.soup.findAll('item')
        self.articles_dicts = [{'title':a.find('title').text,'link':a.link.next_sibling.replace('\n','').replace('\t',''),'description':a.find('description').text,'pubdate':a.find('pubdate').text} for a in self.articles]
        self.urls = [d['link'] for d in self.articles_dicts if 'link' in d]
        self.titles = [d['title'] for d in self.articles_dicts if 'title' in d]
        self.descriptions = [d['description'] for d in self.articles_dicts if 'description' in d]
        self.pub_dates = [d['pubdate'] for d in self.articles_dicts if 'pubdate' in d]

if __name__ == '__main__':

    feed = ReadRss('https://www.jcchouinard.com/author/jean-christophe-chouinard/feed/', headers)
    print(feed.urls)