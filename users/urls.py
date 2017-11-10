from django.conf.urls import url

import movie.views as movie_views
import recommend.views as recommend_views
from . import views, views_auth

urlpatterns = [
    url(r'^$', views.UserListView.as_view(), name='user-list'),
    url(r'^login/$', views_auth.LoginView.as_view(), name='login'),
    url(r'^logout/$', views_auth.LogoutView.as_view(), name='logout'),
    url(r'^register/$', views_auth.RegisterView.as_view(), name='register'),
    url(r'^password-change/$', views_auth.PasswordChangeView.as_view(), name='password-change'),
    url(r'^(?P<username>[-\w]+)/$', views.UserDetailView.as_view(), name='user-detail'),
    url(r'^(?P<username>[-\w]+)/edit/$', views.UserUpdateView.as_view(), name='user-edit'),
    url(r'^(?P<username>[-\w]+)/watchlist/$', movie_views.WatchlistListView.as_view(), name='watchlist'),
    url(r'^(?P<username>[-\w]+)/favourites/$', movie_views.FavouriteListView.as_view(), name='favourite'),

    url(r'^(?P<username>[-\w]+)/recommend/$', recommend_views.recommend, name='recommend'),
    url(r'^(?P<username>[-\w]+)/import/$', views.import_ratings, name='import-ratings'),
    url(r'^(?P<username>[-\w]+)/export$', views.export_ratings, name='export-ratings'),
]