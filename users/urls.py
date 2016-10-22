from django.conf.urls import url
from . import views
import movie.views

urlpatterns = [
    url(r'^(?P<username>\S+)/watchlist/$', movie.views.watchlist, name='watchlist'),
    url(r'^(?P<username>\S+)/favourites/$', movie.views.favourite, name='favourites'),
    url(r'^(?P<username>\S+)/edit/$', views.user_edit, name='user_edit'),
    url(r'^$', views.user_list, name='user_list'),
    url(r'^(?P<username>\S+)/$', views.user_profile, name='user_profile'),



    url(r'^login/', views.login, name='login'),
    url(r'^register/', views.register, name='register'),
    url(r'^logout/', views.logout, name='logout'),
]

# url(r'^id/(?P<const>tt\d{7})/$', views.entry_details_redirect, name='entry_details_redirect'),