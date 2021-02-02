from IPython import display
import math
from pprint import pprint
import pandas as pd
import numpy as np
import nltk
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import seaborn as sns
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
sns.set(style='darkgrid', context='talk', palette='Dark2')

import praw

reddit = praw.Reddit(client_id='mOWIXP7dLTvWbw',
                     client_secret='bHFz-TJq4p9RVuchRkuDhfDLKLCmHg',
                     user_agent='burak_swe')

headlines = set()

for submission in reddit.subreddit('politics').new(limit=2):
    headlines.add(submission.title)


sia = SIA()
results = []

for line in headlines:
    pol_score = sia.polarity_scores(line)
    pol_score['headline'] = line
    results.append(pol_score)

res = results[::len(results)-1]  

print(submission.title)
print(res)
