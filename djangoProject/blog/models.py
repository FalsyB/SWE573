
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import praw
from IPython import display

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA


reddit = praw.Reddit(client_id='mOWIXP7dLTvWbw',
                     client_secret='bHFz-TJq4p9RVuchRkuDhfDLKLCmHg',
                     user_agent='burak_swe')

headlines = set()

for submission in reddit.subreddit('Coronavirus').new(limit=1):
    headlines.add(submission.title)
    display.clear_output()

sia = SIA()
results = []

for line in headlines:
    pol_score = sia.polarity_scores(line)
    pol_score['headline'] = line
    results.append(pol_score)


class Post(models.Model):
    title = submission.title
    content = results
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

class Commentd(models.Model):
    title = models.CharField(max_length=100)
    content = submission.title
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})