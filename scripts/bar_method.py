from IPython import display
import math
from pprint import pprint
import pandas as pd
import numpy as np
import nltk
import sys
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

mood = str(sys.argv[1])
headlines = set()


for submission in reddit.subreddit('Coronavirus').new(limit=500):
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
pprint(results[:3], width=100)
df['label'] = 0
df.loc[df['compound'] > 0.2, 'label'] = 1
df.loc[df['compound'] < -0.2, 'label'] = -1
df.head()

tokenizer = RegexpTokenizer(r'\w+')
stop_words = stopwords.words('english')

def process_text(headlines):
    tokens = []
    for line in headlines:
        toks = tokenizer.tokenize(line)
        toks = [t.lower() for t in toks if t.lower() not in stop_words]
        tokens.extend(toks)
        print(tokens)
    
    return tokens

pos_lines = list(df[df.label == 1].headline)

pos_tokens = process_text(pos_lines)
pos_freq = nltk.FreqDist(pos_tokens)

pos_freq.most_common(20)

df2 = df[['headline', 'label']]
neg_lines = list(df2[df2.label == -1].headline)

neg_tokens = process_text(neg_lines)
neg_freq = nltk.FreqDist(neg_tokens)

neg_freq.most_common(20)

y1_val = [x[1] for x in neg_freq.most_common()]

y1_final = []
for i, k, z in zip(y1_val[0::3], y1_val[1::3], y1_val[2::3]):
    if i + k + z == 0:
        break
    y1_final.append(math.log(i + k + z))

x1_val = [math.log(i+1) for i in range(len(y1_final))]

y_val = [x[1] for x in pos_freq.most_common()]

y_final = []
for i, k, z, t in zip(y_val[0::4], y_val[1::4], y_val[2::4], y_val[3::4]):
    y_final.append(math.log(i + k + z + t))

x_val = [math.log(i + 1) for i in range(len(y_final))]


def plot_method(boo):
   
   if self.plot_method == "n":
      fig = plt.figure(figsize=(10,5))
      plt.xlabel("Words (Log)")
      plt.ylabel("Frequency (Log)")
      plt.title("Word Frequency Distribution (Negative)")
      plt.plot(x1_val, y1_final)
      plt.show()
   
   elif self.plot_method == "p":
        fig = plt.figure(figsize=(10,5))
        plt.xlabel("Words (Log)")
        plt.ylabel("Frequency (Log)")
        plt.title("Word Frequency Distribution (Positive)")
        plt.plot(x_val, y_final)
        plt.show()

plot_method(mood)    




