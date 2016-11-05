from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^explore/$', views.explore, name='explore'),
    # url(r'^about/$', views.about, name='about'),
    # url(r'^search/$', views.search, name='search'),

    url(r'^title/(?P<slug>[\w-]+)/$', views.title_details, name='title_details'),
    url(r'^title/(?P<slug>[\w-]+)/edit/$', views.title_edit, name='title_edit'),
    url(r'^id/(?P<const>tt\d{7})/$', views.title_details_redirect, name='title_details_redirect'),

    url(r'^year/$', views.groupby_year, name='groupby_year'),
    url(r'^genre/$', views.groupby_genre, name='groupby_genre'),
    url(r'^director/$', views.groupby_director, name='groupby_director'),

]
