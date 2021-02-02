
from django.db import models
from django.contrib.auth import get_user_model
import requests
from django.utils.text import slugify
import misaka
from django import template,forms


# Create your models here.

register=template.Library()
User=get_user_model()


class Analysis(models.Model):
    user=models.ForeignKey(User,related_name='analysis',on_delete=models.CASCADE)
    topic=models.CharField(('Topic to be searched in Reddit'),max_length=300)
    analysis_positive=models.IntegerField(blank=False, null=False)
    analysis_negative=models.IntegerField(blank=False,null=False)
    analysis_neutral=models.IntegerField(blank=False,null=False)
    created_at=models.DateTimeField(auto_now=True)
    CHOICES2=[('all','all'),('day','day'),('hour','hour'),('month','month'),('week','week'),('year','year')]
    limit = models.IntegerField('Count of "Top Posts" to be searched in Reddit.')
    time_filter=models.CharField('Reddit API time interval',choices=CHOICES2,max_length=300)

    class Meta():
         ordering = ['-created_at']
