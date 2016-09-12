from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^explore/$', views.explore, name='explore'),
    url(r'^about/$', views.about, name='about'),
    url(r'^search/$', views.search, name='search'),
    url(r'^watchlist/$', views.watchlist, name='watchlist'),

    url(r'^title/(?P<slug>[\w-]+)/$', views.entry_details, name='entry_details'),
    url(r'^id/(?P<const>tt\d{7})/$', views.entry_details_redirect, name='entry_details_redirect'),

    url(r'^year/$', views.entry_groupby_year, name='entry_groupby_year'),
    url(r'^year/(?P<year>\d{4})/$', views.entry_show_from_year, name='entry_show_from_year'),

    url(r'^(?P<year>\d{4})/(?P<month>\d\d*)/$', views.entry_show_rated_in_month, name='entry_show_rated_in_month'),

    url(r'^genre/$', views.entry_groupby_genre, name='entry_groupby_genre'),
    url(r'^genre/(?P<genre>\S+)/$', views.entry_show_from_genre, name='entry_show_from_genre'),

    url(r'^director/$', views.entry_groupby_director, name='entry_groupby_director'),
    url(r'^director/(?P<pk>\d+)/$', views.entry_show_from_director, name='entry_show_from_director'),

    url(r'^rated/(?P<rate>\d+)/$', views.entry_show_from_rate, name='entry_show_from_rate'),
]
