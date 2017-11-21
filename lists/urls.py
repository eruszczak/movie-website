from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ListListView.as_view(), name='home'),
    url(r'^(?P<username>[-\w]+)/watchlist/$', views.WatchlistListView.as_view(), name='watchlist'),
    url(r'^(?P<username>[-\w]+)/favourites/$', views.FavouriteListView.as_view(), name='favourite'),
]
