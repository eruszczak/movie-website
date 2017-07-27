from django.conf.urls import url

import movie.views
import recommend.views
from . import views, views_auth

urlpatterns = [
    url(r'^$', views.UserListView.as_view(), name='user-list'),

    url(r'^login/$', views_auth.AuthLoginView.as_view(), name='login-view'),
    url(r'^logout/$', views_auth.AuthLogoutView.as_view(), name='logout-view'),
    url(r'^register/$', views_auth.AuthRegisterView.as_view(), name='register-view'),
    url(r'^password-change/$', views_auth.AuthPasswordChangeView.as_view(), name='password-change-view'),

    url(r'^(?P<username>[-\w]+)/$', views.UserDetailView.as_view(), name='user-detail'),
    url(r'^(?P<username>[-\w]+)/edit/$', views.UserUpdateView.as_view(), name='user-edit'),

    url(r'^(?P<username>[-\w]+)/watchlist/$', movie.views.watchlist, name='watchlist'),
    url(r'^(?P<username>[-\w]+)/favourites/$', movie.views.favourite, name='favourite'),
    url(r'^(?P<username>[-\w]+)/recommend/$', recommend.views.recommend, name='recommend'),

    url(r'^(?P<username>[-\w]+)/import/$', views.import_ratings, name='import-ratings'),
    url(r'^(?P<username>[-\w]+)/export$', views.export_ratings, name='export-ratings'),
]