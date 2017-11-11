from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^explore/$', views.TitleListView.as_view(), name='title-list'),
    url(r'^title/(?P<const>tt\d+)/(?P<slug>[\w-]+)/$', views.TitleDetailView.as_view(), name='title-detail'),
    url(r'^title/(?P<const>tt\d+)/$', views.TitleRedirectView.as_view(), name='title-redirect'),
    url(r'^rating/(?P<pk>\d+)/edit/$', views.RatingUpdateView.as_view(), name='rating-update'),
    url(r'^year/', views.GroupByYearView.as_view(), name='group-year'),
    url(r'^genre/$', views.GroupByGenreView.as_view(), name='group-genre'),
    url(r'^director/$', views.GroupByDirectorView.as_view(), name='group-director'),
]
