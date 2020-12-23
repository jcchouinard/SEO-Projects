import json
import praw
import requests

subr = 'pythonsandlot'
credentials = 'client_secrets.json'

with open(credentials) as f:
    creds = json.load(f)

reddit = praw.Reddit(client_id=creds['client_id'],
                     client_secret=creds['client_secret'],
                     user_agent=creds['user_agent'],
                     redirect_uri=creds['redirect_uri'],
                     refresh_token=creds['refresh_token'])

print(reddit.user.me())

subreddit = reddit.subreddit(subr)

title = 'Just Made My first Post on Reddit Using Python.'
selftext = '''
I am learning how to use the Reddit API with Python using the PRAW wrapper.
By following the tutorial on https://www.jcchouinard.com/post-on-reddit-with-python/
This post was uploaded from my Python Script
'''

subreddit.submit(title,selftext=selftext)

