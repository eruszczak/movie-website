from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.EntryListView.as_view(), name='entry_list'),
    url(r'^detail/(?P<slug>[\w-]+)/$', views.EntryDetailView.as_view(), name='entry_detail'),
    url(r'^genre/$', views.GenreListView.as_view(), name='genre_list'),
    url(r'^g/$', views.Genre2.as_view(), name='genre_list'),
    url(r'^rated/$', views.RateListView.as_view(), name='rate_list'),
    url(r'^year/$', views.YearListView.as_view(), name='year_list'),
    url(r'^month/$', views.MonthListView.as_view(), name='month_list'),

    url(r'^update/(?P<slug>[\w-]+)/$', views.WatchAgainUpdateView.as_view(), name='watch_again'),
    # url(r'^rated/(?P<rate>\d+)/$', views.RateListView.as_view(), name='rate_detail'),
]