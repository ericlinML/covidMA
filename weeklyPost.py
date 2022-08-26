import numpy as np
import pandas as pd
from datetime import date, timedelta

import json
import praw
import requests
import tweepy

def createLastRow(df):
    lastRow = df.dropna().iloc[-1]
    return lastRow

def getDate(row, *args):
    if args:
        return str(row[args[0]])[:10]
    else:
        return str(row['Date'])[:10]


runDay = date.today()
yesterday = runDay - timedelta(days=1)
dayString = yesterday.strftime("%B-%#d-%Y")

df = pd.read_excel(f'https://www.mass.gov/doc/covid-19-raw-data-{dayString}/download', sheet_name=None)

# Cases
casesDf = df['Cases (Report Date)'].drop(axis=1, labels='Estimated active cases')
casesRow = createLastRow(casesDf)

cases = casesRow['Positive New']

casesDate = getDate(casesRow)


# Positivity
posRow = createLastRow(df['Weekly_Statewide'])

positivity = posRow['Percent Positivity'] * 100

# 14d collection ending on stated date but is reported only by the current date
positivityDate = getDate(posRow, 'End Date')


# Deaths
deathsRow = createLastRow(df['DeathsReported (Report Date)'])
deaths = deathsRow['DeathsConfNew']

deathsDate = getDate(deathsRow)


# Hospitalizations
hospRow = createLastRow(df['Hospitalization from Hospitals'])

totalCOVIDhosp = int(hospRow['Total number of COVID patients in hospital today'])

newCOVIDhosp = int(hospRow['Net new number of COVID patients in hospital today'])

covidOnlyHosp = int(hospRow['Hospitalized primarily due to COVID-19 related illness'])

hospDate = getDate(hospRow)


cred = 'client_secrets.json'
with open(cred) as f:
    creds = json.load(f)


# Post to reddit
reddit = praw.Reddit(
    client_id = creds['client_id'],
    client_secret=creds['client_secret'],
    user_agent=creds['user_agent'],
    redirect_uri=creds['redirect_uri'],
    refresh_token=creds['refresh_token']
    )

print(reddit.user.me())

#subr = 'CoronavirusMa'
subr = 'test'
subreddit = reddit.subreddit(subr)
title = f'{casesDate} Massachusetts COVID weekly data: {cases} new cases at {round(positivity, 2)}% test positivity, {deaths} new deaths, {totalCOVIDhosp} total individuals hospitalized with COVID'

text = f"""  
This data is from the https://www.mass.gov/info-details/covid-19-response-reporting COVID-19 Raw Data file. Since July 8th, 2022, this data is reported weekly and represents weekly totals as opposed to daily totals. 

**Data supplied with dates:**
- New cases this week: {cases} ({casesDate})
- Most recent test positivity data: {round(positivity, 2)}% (from a 2 week period ending on {positivityDate})
- New deaths this week: {deaths} ({deathsDate})
- Total COVID patients in hospital: {totalCOVIDhosp} ({hospDate})
- Patients hospitalized primarily due to COVID: {covidOnlyHosp} ({hospDate})

Please note that there is some lag with how some of the data has been reported. 
"""

subreddit.submit(title, selftext = text)
#subreddit.submit(title, selftext = text, flair_id='1d8891e0-80e4-11ea-8ad7-0e20863e7c8d')


# Post to Twitter via v2 API
twitter = tweepy.Client(
    bearer_token=creds['twitter_bearer_token'],
    consumer_key=creds['twitter_api_key'],
    consumer_secret=creds['twitter_api_secret'],
    access_token=creds['twitter_access_token'],
    access_token_secret=creds['twitter_access_secret']
)

tweetText = f"""
Weekly Massachusetts COVID data published on {casesDate}:

{cases} new cases at {round(positivity, 2)}% test positivity
{deaths} new deaths
{totalCOVIDhosp} total individuals hospitalized with COVID
{covidOnlyHosp} hospitalized primarily for COVID

From mass.gov's weekly COVID-19 Raw Data file https://www.mass.gov/info-details/covid-19-response-reporting
"""

twitter.create_tweet(text=tweetText)