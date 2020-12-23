'''
pip install praw
pip install feedparser
'''
import feedparser
import json
import praw
import random
import requests
import time 

from bs4 import BeautifulSoup

subr = 'pythonsandlot'
credentials = 'client_secrets.json'

with open(credentials) as f:
    creds = json.load(f)


# Option 1: PRAW stores your password
# reddit = praw.Reddit(client_id=creds['client_id'],
#                      client_secret=creds['client_secret'],
#                      user_agent=creds['user_agent'],
#                      username=creds['username'],
#                      password=creds['password'])

# Option 2: Use Refresh token (recommended)
reddit = praw.Reddit(client_id=creds['client_id'],
                     client_secret=creds['client_secret'],
                     user_agent=creds['user_agent'],
                     redirect_uri=creds['redirect_uri'],
                     refresh_token=creds['refresh_token'])

print(reddit.user.me())

subreddit = reddit.subreddit(subr)
requirements = subreddit.post_requirements()['is_flair_required']

subs = []
for sub in subreddit.hot(limit=500):
    print(f'sub.title: {sub.title}')
    print(f'sub.score: {sub.score}') 
    print(f'sub.selftext: {sub.selftext}')
    print(f'sub.url: {sub.url}')
    print(f'sub.view_count: {sub.view_count}')
    #print(f'sub.upvote: {sub.upvote}')
    print(f'sub.upvote_ratio: {sub.upvote_ratio}')
    print(f'sub.num_comments: {sub.num_comments}')
    print(f'sub.subreddit: {sub.subreddit}')
    print(f'sub.subreddit_id: {sub.subreddit_id}')
    print(f'sub.subreddit_name_prefixed: {sub.subreddit_name_prefixed}')
    print(f'sub.subreddit_subscribers: {sub.subreddit_subscribers}')



#search subreddit for keywords
subreddit = reddit.subreddit('all')


subs = []
for sub in subreddit.search('python+seo',time_filter='month'):
    subs.append({'id':sub.id,'score':sub.score,'title':sub.title,'url':sub.url,'subreddit_name_prefixed':sub.subreddit_name_prefixed,'num_comments':sub.num_comments})

subs = sorted(subs, key = lambda x: x['score'], reverse=True)
subs[:10]
sorted(subs.items(), key=lambda x: x['score'], reverse=True)


sub_ids = []
for submission in subreddit.hot(limit = 5): # Define the limit here and filter method
    sub_ids.append(submission.id)

top_level_comments = []
second_level_comments = []
title = []
selftext = []
for sub_id in sub_ids:
    submission = reddit.submission(id = sub_id)
    title.append(submission.title) # Get submission title
    selftext.append(submission.selftext) # Get submission content
    submission.comments.replace_more(limit = None)
    for top_level_comment in submission.comments:
        top_level_comments.append(top_level_comment.body) # Get top-level comments
        for second_level_comment in top_level_comment.replies:
            second_level_comments.append(second_level_comment.body) # Ge

for submission in reddit.subreddit("redditdev+learnpython").top("all"):
    print(submission)

for submission in reddit.subreddit("all-redditdev").new():
    print(submission)




##########

# Parse feed to get post
xml = feedparser.parse('https://www.jcchouinard.com/feed/')
entry = xml.entries

posts = {}
for i in range(len(entry)):
    posts[entry[i].link] = {'title':entry[i].title,'description':''}

for k in posts.keys():
    try:
        r = requests.get(k)
    except Exception as e:
        print(e)

    soup = BeautifulSoup(r.text, 'html.parser')
    metatags = soup.find_all('meta', {'name': 'description'})
    posts[k]['description'] = metatags[0]['content']

for k,v in posts.items():
    appender = [
        'Here is the link to the post ',
        'You can read the article here ',
        'Read the story on '
    ]
    text = f'. {appender[random.randint(0,2)]} {k}.'
    selftext = v['description'] + text
    title = v['title']
    reddit.subreddit(subr).submit(title,selftext=selftext)
    time.sleep(3)


# Extract GSC for top keywords
# Search Reddit for Rising Sub containing each keyword
# Send alert