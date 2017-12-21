from django.conf.urls import url

from . import views, views_auth

urlpatterns = [
    url(r'^$', views.UserListView.as_view(), name='user-list'),
    url(r'^login/$', views_auth.LoginView.as_view(), name='login'),
    url(r'^logout/$', views_auth.LogoutView.as_view(), name='logout'),
    url(r'^register/$', views_auth.RegisterView.as_view(), name='register'),
    # url(r'^password-change/$', views_auth.PasswordChangeView.as_view(), name='password-change'),
    url(r'^(?P<username>[-\w]+)/$', views.UserDetailView.as_view(), name='user-detail'),
    url(r'^(?P<username>[-\w]+)/edit/$', views.UserUpdateView.as_view(), name='user-edit'),

    # url(r'^(?P<username>[-\w]+)/recommend/$', recommend_views.recommend, name='recommend'),
]
