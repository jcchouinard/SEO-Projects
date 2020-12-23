import json 
import pandas as pd
import requests
 
subreddit = 'python'
limit = 1
timeframe = 'month' #hour, day, week, month, year, all
listing = 'top' # controversial, best, hot, new, random, rising, top
 
def get_reddit(subreddit,listing,limit,timeframe):
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?limit={limit}&t={timeframe}'
        request = requests.get(base_url, headers = {'User-agent': 'yourbot'})
    except:
        print('An Error Occured')
    return request.json()

def show_tags(r):
    '''
    show what tags you can use
    '''
    for post in r['data']['children']:
        for k in post['data'].keys():
            print(k)

def get_post_titles(r):
    '''
    Get a List of post titles
    '''
    posts = []
    for post in r['data']['children']:
        x = post['data']['title']
        posts.append(x)
    return posts

def get_results(r):
    '''
    Create a DataFrame Showing Title, URL, Score and Number of Comments.
    '''
    myDict = {}
    for post in r['data']['children']:
        myDict[post['data']['title']] = {'url':post['data']['url'],'score':post['data']['score'],'comments':post['data']['num_comments']}
    df = pd.DataFrame.from_dict(myDict, orient='index')
    return df

if __name__ == '__main__':
    r = get_reddit(subreddit,listing,limit,timeframe)
    posts = get_post_titles(r)
    df = get_results(r)