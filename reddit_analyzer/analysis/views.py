from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import generic
from . import models
from django.shortcuts import get_object_or_404
from django.contrib import messages
import praw
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from praw.models import MoreComments
from django.contrib.auth import get_user_model
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import redirect
from django import template
from prawcore import NotFound
from textblob import TextBlob
import matplotlib.pyplot as plt



text=' '
register = template.Library()
reddit = praw.Reddit(client_id='mOWIXP7dLTvWbw',
                     client_secret='bHFz-TJq4p9RVuchRkuDhfDLKLCmHg',
                     user_agent='burak_swe')

sia = SentimentIntensityAnalyzer()

# Create your views here.

class AnalysisView(generic.CreateView,LoginRequiredMixin):

    fields=('topic','limit','time_filter')
    model=models.Analysis

    def form_valid(self,form):

            self.object = form.save(commit=False)
            global reddit
            global text
            text=''
            top_posts = reddit.subreddit(self.object.topic).top(self.object.time_filter, limit=self.object.limit)
            try:
                result_dict=AnalysisDone(top_posts)
                result_vict=AnalysisTextBlob(top_posts)

            except NotFound:
                return HttpResponseRedirect("fail")

            if(result_dict['positive']==0 and result_dict['negative']==0 and result_dict['neutral'] <3):
                return HttpResponseRedirect("fail")

            else:

                self.object.user=self.request.user
                self.object.analysis_neutral=result_dict['neutral']
                self.object.analysis_negative=result_dict['negative']
                self.object.analysis_positive=result_dict['positive']
                self.object.save()
                return HttpResponseRedirect("results")


class FailView(generic.TemplateView,LoginRequiredMixin):
    template_name="analysis/fail.html"


class ResultsView(generic.TemplateView,LoginRequiredMixin):
    template_name="analysis/results.html"
    def get_context_data(self, **kwargs):
        analysis=models.Analysis.objects.filter(user=self.request.user).order_by('-created_at')[0]
        context = super(ResultsView, self).get_context_data(**kwargs)
        context['positive'] = analysis.analysis_positive
        context['negative'] = analysis.analysis_negative
        context['neutral']=analysis.analysis_neutral
        context['topic']=analysis.topic
        return context

class HistoryView(generic.ListView,LoginRequiredMixin):
    context_object_name='h_analysis'
    model=models.Analysis

    def get_queryset(self):
        return models.Analysis.objects.filter(user=self.request.user)


def AnalysisDone(top_posts):
    for submission in top_posts:
        sub_entries_nltk = {'negative': 0, 'positive' : 0, 'neutral' : 0}
        sub_entries_textblob = {'negative': 0, 'positive' : 0, 'neutral' : 0}
        text_blob_sentiment(submission.title, sub_entries_textblob)
        nltk_sentiment(submission.title, sub_entries_nltk)
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

        return sub_entries_nltk

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
