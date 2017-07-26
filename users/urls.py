from django.conf.urls import url

import movie.views
import recommend.views
from . import views, views_auth

urlpatterns = [
    # url(r'^$', views.user_list, name='user-list'),
    url(r'^$', views.UserListView.as_view(), name='user-list'),

    url(r'^login/', views_auth.AuthLoginView.as_view(), name='login-view'),
    url(r'^register/', views_auth.AuthRegisterView.as_view(), name='register-view'),
    url(r'^password-change/', views_auth.AuthPasswordChangeView.as_view(), name='password-change-view'),
    url(r'^logout/', views_auth.AuthLogoutView.as_view(), name='logout-view'),
    url(r'^import', views.import_ratings, name='import_ratings'),

    url(r'^(?P<username>[-\w]+)/$', views.user_profile, name='user_profile'),
    url(r'^(?P<username>[-\w]+)/export$', views.export_ratings, name='export_ratings'),
    url(r'^(?P<username>[-\w]+)/edit/$', views.user_edit, name='user_edit'),

    url(r'^(?P<username>[-\w]+)/watchlist/$', movie.views.watchlist, name='watchlist'),
    url(r'^(?P<username>[-\w]+)/favourites/$', movie.views.favourite, name='favourite'),
    url(r'^(?P<username>[-\w]+)/recommend/$', recommend.views.recommend, name='recommend'),
]