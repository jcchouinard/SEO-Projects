#!/usr/bin/env python
'''
@author:    Daniel Heredia Mejias 
@website:   danielherediamejias.com

Published on:
https://www.jcchouinard.com/pagespeed-api-and-lighthouse-forecasting/(ouvre un nouvel onglet)
'''
import time

from selenium import webdriver
import urllib.request, json

device = "mobile"
page = "https://www.danielherediamejias.com/"

url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=" + page + "&strategy=" + device + "&locale=en"

try:
    response = urllib.request.urlopen(url)
except Exception as e:
    print(e)

data = json.loads(response.read()) 


fcp_time = data["lighthouseResult"]["audits"]["first-contentful-paint"]["displayValue"]
speed_index = data["lighthouseResult"]["audits"]["speed-index"]["displayValue"]
lcp = data["lighthouseResult"]["audits"]["largest-contentful-paint"]["displayValue"]
time_interactive = data["lighthouseResult"]["audits"]["interactive"]["displayValue"]
blocking_time_duration = data["lighthouseResult"]["audits"]["total-blocking-time"]["displayValue"]
cls = data["lighthouseResult"]["audits"]["cumulative-layout-shift"]["displayValue"]
overall_score = int(data["lighthouseResult"]["categories"]["performance"]["score"] * 100)


fcp_time = ["First Contentful Time" ,int(float(fcp_time.replace("\xa0s", ""))*1000)]
speed_index = ["Speed Index", int(float(speed_index.replace("\xa0s", ""))*1000)]
time_interactive = ["Time to interactive", int(float(time_interactive.replace("\xa0s", ""))*1000)]
blocking_time_duration = ["Total Blocking Time", int(blocking_time_duration.replace("\xa0ms", ""))]
lcp = ["Large Contentful Paint", int(float(lcp.replace("\xa0s", ""))*1000)]
cls = ["Cumulative Layout Shift", round(float(cls), 2)]

list = [fcp_time, speed_index, time_interactive, blocking_time_duration, lcp, cls]

driver=webdriver.Chrome() 
driver.get('https://googlechrome.github.io/lighthouse/scorecalc/#FCP=' + str(list[0][1]) + '&SI=' + str(list[1][1]) + '&LCP=' + str(list[4][1]) + '&TTI=' + str(list[2][1]) + '&TBT=' + str(list[3][1]) + '&CLS=' + str(list[5][1]) + '&device=” +device + “&version=6')
time.sleep(3)
element = driver.find_element_by_class_name("lh-gauge__percentage")
finalscore = int(element.text)

driver.quit()

differenceslist = []
numLoops = len(list)

print('Adding a 50% increase to each metrics to check score improvement\n')
print(f'This loop will fetch the Lighthouse {numLoops} times\n')
for x in range(numLoops):
    print(f'Testing improvement on {list[x][0]}')
    oldnumber = list[x][1]
    list[x][1] = list[x][1] - list[x][1] * 0.5 
    driver = webdriver.Chrome() 
    driver.get('https://googlechrome.github.io/lighthouse/scorecalc/#FCP='  + str(list[0][1]) + '&SI=' + str(list[1][1]) + '&LCP=' + str(list[4][1]) + '&TTI=' + str(list[2][1]) + '&TBT=' + str(list[3][1]) + '&CLS=' + str(list[5][1]) + '&device=' + device + '&version=6')
    time.sleep(20)
    element = driver.find_element_by_class_name("lh-gauge__percentage")
    finalscore = int(element.text)
    driver.quit()   
    
    differenceslist.append(finalscore - overall_score)
    list[x][1] = oldnumber

print("\nWoking on " + str(list[differenceslist.index(max(differenceslist))][0]) + " would improve performance " + str(max(differenceslist)) + " points." )
for x in range (len(differenceslist)):
    print("If you improve 50% of " + str(list[x][0]) + " you will improve " + str(differenceslist[x]) + " points your overall score")
