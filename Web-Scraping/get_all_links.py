from lxml import html
import requests

url = 'https://example.com'

page = requests.get(url)
webpage = html.fromstring(page.content)

links = webpage.xpath('//a/@href')
links