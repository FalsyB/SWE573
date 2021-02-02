from django.urls import path,re_path
from . import views

app_name='analysis'

urlpatterns=[
    path('',views.AnalysisView.as_view(),name='analysis_home'),
    path('history/',views.HistoryView.as_view(),name='history'),
    path('results/',views.ResultsView.as_view(),name='results'),
    path('fail/',views.FailView.as_view(),name='fail'),

]
