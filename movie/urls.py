from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^explore/$', views.explore, name='explore'),
    # url(r'^about/$', views.about, name='about'),
    # url(r'^search/$', views.search, name='search'),
    # url(r'^watchlist/$', views.watchlist, name='watchlist'),
    # # url(r'^watchlist-imdb/$', views.imdb_watchlist, name='imdb_watchlist'),
    # url(r'^favourite/$', views.favourite, name='favourites'),
    #
    url(r'^title/(?P<slug>[\w-]+)/$', views.title_details, name='entry_details'),
    url(r'^title/(?P<slug>[\w-]+)/edit/$', views.title_edit, name='entry_edit'),
    url(r'^id/(?P<const>tt\d{7})/$', views.title_details_redirect, name='entry_details_redirect'),

    url(r'^year/$', views.groupby_year, name='entry_groupby_year'),
    url(r'^genre/$', views.groupby_genre, name='entry_groupby_genre'),
    url(r'^director/$', views.groupby_director, name='entry_groupby_director'),

    url(r'^rated/(?P<rate>\d+)/$', views.titles_from_rate, name='entry_show_from_rate'),
    url(r'^(?P<year>\d{4})/(?P<month>\d\d*)/$', views.titles_rated_in_month, name='entry_show_rated_in_month'),

]
