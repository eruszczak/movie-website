from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^entry/(?P<const>tt\d{7})/$', views.entry_details, name='entry_details'),
    url(r'^year/$', views.entry_groupby_year, name='entry_groupby_year'),
    url(r'^year/(?P<year>\d{4})/$', views.entry_show_from_year, name='entry_show_from_year'),
]
