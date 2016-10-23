from django.conf.urls import url
from . import views
import movie.views

urlpatterns = [
    url(r'^$', views.user_list, name='user_list'),
    url(r'^(?P<username>[-\w]+)/$', views.user_profile, name='user_profile'),
    url(r'^(?P<username>[-\w]+)/edit/$', views.user_edit, name='user_edit'),
    url(r'^(?P<username>[-\w]+)/watchlist/$', movie.views.watchlist, name='watchlist'),
    url(r'^(?P<username>[-\w]+)/favourites/$', movie.views.favourite, name='favourites'),

]