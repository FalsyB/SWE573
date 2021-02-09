from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from . import models
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
import praw
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import redirect
from django import template
from prawcore import NotFound
from textblob import TextBlob
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

import matplotlib.pyplot as plt
from .models import Analysis




text=' '
register = template.Library()
reddit = praw.Reddit(client_id='mOWIXP7dLTvWbw',
                     client_secret='bHFz-TJq4p9RVuchRkuDhfDLKLCmHg',
                     user_agent='burak_swe')

sia = SentimentIntensityAnalyzer()

# Create your views here.

class AnalysisView(generic.CreateView,LoginRequiredMixin):

    fields=('topic','limit',)
    model=models.Analysis

    def form_valid(self,form):

            self.object = form.save(commit=False)
            global reddit
            global text
            text=''
            top_posts = reddit.subreddit(self.object.topic).top("day", limit=self.object.limit)
            #for item in reddit.subreddit("test").gilded():
                #mitem = sum(item)
            try:
                result_dict,scores=AnalysisDone(top_posts)
                #result_dict, token_count=AnalysisDone(top_posts)
                #result_vict=AnalysisTextBlob(top_posts)

            except NotFound:
                return HttpResponseRedirect("fail")

            if(result_dict['positive']==0 and result_dict['negative']==0 and result_dict['neutral'] <3):
                return HttpResponseRedirect("fail")

            else:

                self.object.user=self.request.user
                self.object.analysis_neutral=result_dict['neutral']
                self.object.analysis_negative=result_dict['negative']
                self.object.analysis_positive=result_dict['positive']
                score_array_str = [str(i) for i in scores]
                score_str = ','.join(score_array_str)
                self.object.score=score_str
                self.object.save()
                return HttpResponseRedirect("results")


class FailView(generic.TemplateView,LoginRequiredMixin):
    template_name="analysis/fail.html"


class ResultsView(generic.TemplateView,LoginRequiredMixin):
    template_name="analysis/results.html"
    def get_context_data(self, **kwargs):
        analysis=models.Analysis.objects.filter(user=self.request.user).order_by('-created_at')[0]
        data = []
        labels = []
        context = super(ResultsView, self).get_context_data(**kwargs)
        context['positive'] = analysis.analysis_positive
        context['negative'] = analysis.analysis_negative
        context['neutral']=analysis.analysis_neutral
        context['topic']= analysis.topic
        context['score'] = analysis.score
        context['data']= [analysis.analysis_positive, analysis.analysis_negative, analysis.analysis_neutral]
        context['labels']= ['Positive Comments', 'Negative Comments', 'Neutral Comments']
        return context
class HistoryView(generic.ListView,LoginRequiredMixin):
    context_object_name='h_analysis'
    model=models.Analysis

    def get_queryset(self):
        return models.Analysis.objects.filter(user=self.request.user)



def AnalysisDone(top_posts):
    scores =[]
    for submission in top_posts:
        sub_entries_nltk = {'negative': 0, 'positive' : 0, 'neutral' : 0}
        sub_entries_textblob = {'negative': 0, 'positive' : 0, 'neutral' : 0}
        text_blob_sentiment(submission.title, sub_entries_textblob)
        nltk_sentiment(submission.title, sub_entries_nltk)
        scores.append(submission.score)
        #print(type(sub_entries_nltk))
        submission_comm = reddit.submission(id=submission.id)

        for count, top_level_comment in enumerate(submission_comm.comments):
            count_comm = 0
            try :
                global text
                text+=top_level_comment.body+','

                nltk_sentiment(top_level_comment.body, sub_entries_nltk)
                text_blob_sentiment(top_level_comment.body, sub_entries_textblob)
                replies_of(top_level_comment,
                           count_comm,
                           sub_entries_nltk,
                           )
            except:
                continue
    '''tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text.lower())
    token_set = set(tokens)
    #print(token_set)
    token_count = []
    for token in token_set:
        token_count.append(tokens.count(token))
        #print(token_count)
    zipped_list = zip(token_count, token_set)
    stop_words = stopwords.words('english')
    sorted_list = sorted(zipped_list,reverse=True)
    sorted_tokens = [t for _, t in sorted_list if t not in stop_words]
    print(sorted_tokens)
    sorted_top_tokens = sorted_tokens[:20]'''
    reddit_coloring = np.array(Image.open("snoo.jpg"))
    wc = WordCloud(background_color="black", max_words=400, mask=reddit_coloring,max_font_size=65,random_state=22)
    wc.generate(text)
    wc.to_file("static/images/wordcloud.png")
    image_colors=ImageColorGenerator(reddit_coloring)

    return sub_entries_nltk,scores

def AnalysisTextBlob(top_posts):
    for submission in top_posts:
        sub_entries_textblob = {'negative': 0, 'positive' : 0, 'neutral' : 0}
        text_blob_sentiment(submission.title, sub_entries_textblob)
        submission_comm = reddit.submission(id=submission.id)

        for count, top_level_comment in enumerate(submission_comm.comments):
            count_comm = 0
            try :
                global text
                text+=top_level_comment.body+','
                text_blob_sentiment(top_level_comment.body, sub_entries_textblob)
                replies_of(top_level_comment,
                           count_comm,
                           sub_entries_textblob,
                           )
            except:
                continue

        return sub_entries_textblob


def nltk_sentiment(review, sub_entries_nltk):
    vs = sia.polarity_scores(review)
    if not vs['neg'] > 0.05:
        if vs['pos'] - vs['neg'] > 0:
            sub_entries_nltk['positive'] = sub_entries_nltk['positive'] + 1
            return 'Positive'
        else:
            sub_entries_nltk['neutral'] = sub_entries_nltk['neutral'] + 1
            return 'Neutral'

    elif not vs['pos'] > 0.05:
        if vs['pos'] - vs['neg'] <= 0:
            sub_entries_nltk['negative'] = sub_entries_nltk['negative'] + 1
            return 'Negative'
        else:
            sub_entries_nltk['neutral'] = sub_entries_nltk['neutral'] + 1
            return 'Neutral'
    else:
        sub_entries_nltk['neutral'] = sub_entries_nltk['neutral'] + 1
        return 'Neutral'

def text_blob_sentiment(review, sub_entries_textblob):
    analysis = TextBlob(review)
    if analysis.sentiment.polarity >= 0.0001:
        if analysis.sentiment.polarity > 0:
            sub_entries_textblob['positive'] = sub_entries_textblob['positive'] + 1
            return 'Positive'

    elif analysis.sentiment.polarity <= -0.0001:
        if analysis.sentiment.polarity <= 0:
            sub_entries_textblob['negative'] = sub_entries_textblob['negative'] + 1
            return 'Negative'
    else:
        sub_entries_textblob['neutral'] = sub_entries_textblob['neutral'] + 1
        return 'Neutral'


def replies_of(top_level_comment, count_comment, sub_entries_nltk):
    if len(top_level_comment.replies) == 0:
        count_comment = 0
        return
    else:
        for num, comment in enumerate(top_level_comment.replies):
            try:
                count_comment += 1
                nltk_sentiment(comment.body, sub_entries_nltk)
            except:
                continue
            replies_of(comment, count_comment ,sub_entries_nltk)
#
