import numpy as np
import pandas as pd
import datetime

import json
import praw
import requests
import tweepy

def getDate(varKey, colIndex):
    date = df[varDict[varKey]].columns[colIndex]
    if isinstance(date, datetime.datetime):
        return(str(date)[:10])
    elif isinstance(date, str):
        return(str(datetime.datetime.strptime(date[:-1], "%m/%d/%Y"))[:10])
    else:
        return f'Date parsing error for {varKey}'

runDay = datetime.date.today()
yesterday = runDay - datetime.timedelta(days=1)
dayString = yesterday.strftime("%B-%#d-%Y")

df = pd.read_excel(f"https://www.mass.gov/doc/chapter-93-state-numbers-daily-report-{dayString}/download", sheet_name=None)

varDict = {'Tested': 'Tested_24hours', 'Positive':'Pos_Last24', 'Died':'Died_last24'}

printDict = {}
for varKey in varDict.keys():
    todayData = df[varDict[varKey]].iloc[0,-1]
    todayDate = getDate(varKey, -1)
    lastWeekData = df[varDict[varKey]].iloc[0,-6]
    lastWeekDate = getDate(varKey, -6)
    
    printDict[varKey] = [todayDate, todayData, lastWeekDate, lastWeekData]

today = printDict['Tested'][0]

redditText = f"""
**Daily MA Covid Numbers reported from {printDict['Tested'][0]}:**

Individuals who tested positive: {printDict['Positive'][1]} ({printDict['Positive'][0]}) \n
Data from 7d prior for reference: {printDict['Positive'][3]} ({printDict['Positive'][2]})


Total individuals who tested: {printDict['Tested'][1]} ({printDict['Tested'][0]}) \n
Data from 7d prior for reference: {printDict['Tested'][3]} ({printDict['Tested'][2]})


Deaths: {printDict['Died'][1]} ({printDict['Died'][0]}) \n
Data from 7d prior for reference: {printDict['Died'][3]} ({printDict['Died'][2]})


Data is drawn from the https://www.mass.gov/info-details/covid-19-response-reporting Chapter93 State Numbers Daily Report file. This data is still being reported daily on weekdays by Mass.gov.

The test counts (total and positive only) include all test types that are reported that day. An individual who takes multiple tests of different types in one day is only counted once.
The death counts can differ from the dashboard since the death counts reported here are not finalized (dashboard numbers are finalized). Deaths which are reported on Friday are rolled into Monday's reported numbers. Deaths reported from Saturday, Sunday, and Monday are rolled into Tuesday's reported numbers.

Because of these peculiarities in reporting, I only show the data from 7d prior as a reference point. I defer graphical representation of COVID data to oldgrimalkin's beautiful visualizations.
"""


# Post to reddit
cred = 'client_secrets.json'
with open(cred) as f:
    creds = json.load(f)

reddit = praw.Reddit(
    client_id = creds['client_id'],
    client_secret=creds['client_secret'],
    user_agent=creds['user_agent'],
    redirect_uri=creds['redirect_uri'],
    refresh_token=creds['refresh_token']
    )

print(reddit.user.me())

subr = 'CoronavirusMa'
subreddit = reddit.subreddit(subr)
title = f"{today} Massachusetts COVID daily data: {printDict['Positive'][1]} new cases, {printDict['Died'][1]} new deaths, {printDict['Tested'][1]} individuals tested"

subreddit.submit(title, selftext = redditText, flair_id='1d8891e0-80e4-11ea-8ad7-0e20863e7c8d')


# Post to Twitter via v2 API
twitter = tweepy.Client(
    bearer_token=creds['twitter_bearer_token'],
    consumer_key=creds['twitter_api_key'],
    consumer_secret=creds['twitter_api_secret'],
    access_token=creds['twitter_access_token'],
    access_token_secret=creds['twitter_access_secret']
)

tweetText = f"""
{today} Massachusetts COVID daily data: 
{printDict['Positive'][1]} new cases ({printDict['Positive'][3]} on {printDict['Positive'][2]})
{printDict['Died'][1]} new deaths ({printDict['Died'][3]} on {printDict['Died'][2]})
{printDict['Tested'][1]} individuals tested ({printDict['Tested'][3]} on {printDict['Tested'][2]})

Source: yet-to-be finalized data released weekdays from the Chapter93 State Daily Report https://www.mass.gov/info-details/covid-19-response-reporting
"""

twitter.create_tweet(text=tweetText)