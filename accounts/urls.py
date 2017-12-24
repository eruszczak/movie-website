from django.conf.urls import url

from . import views
import lists.views as lists_views


urlpatterns = [
    url(r'^$', views.UserListView.as_view(), name='user-list'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^password-change/$', views.PasswordChangeView.as_view(), name='password-change'),
    url(r'^settings/$', views.UserUpdateView.as_view(), name='user-edit'),
    url(r'^(?P<username>[-\w]+)/$', views.UserDetailView.as_view(), name='user-detail'),
    url(r'^(?P<username>[-\w]+)/watchlist/$', lists_views.WatchlistListView.as_view(), name='watchlist-list'),
    url(r'^(?P<username>[-\w]+)/favourites/$', lists_views.FavouriteListView.as_view(), name='favourite-list'),
]
