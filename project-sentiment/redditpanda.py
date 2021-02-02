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

for submission in reddit.subreddit('politics').new(limit=None):
    headlines.add(submission.title)
    display.clear_output()

sia = SIA()
results = []

for line in headlines:
    pol_score = sia.polarity_scores(line)
    pol_score['headline'] = line
    results.append(pol_score)




df = pd.DataFrame.from_records(results)
df.head()
#pprint(results[:3], width=100)
df['label'] = 0
df.loc[df['compound'] > 0.2, 'label'] = 1
df.loc[df['compound'] < -0.2, 'label'] = -1
df.head()

fig, ax = plt.subplots(figsize=(8, 8))

counts = df.label.value_counts(normalize=True) * 100

sns.barplot(x=counts.index, y=counts, ax=ax)

ax.set_xticklabels(['Negative', 'Neutral', 'Positive'])
ax.set_ylabel("Percentage")



fig.savefig('test.pdf')


