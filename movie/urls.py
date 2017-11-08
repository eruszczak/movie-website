from django.conf.urls import url
from . import views, views_class

urlpatterns = [
    url(r'^title/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.TitleDetailView.as_view(), name='title-detail'),

    url(r'^$', views.home, name='home'),
    url(r'^explore/$', views.explore, name='explore'),

    url(r'^title/(?P<slug>[\w-]+)/$', views.title_details, name='title_details'),
    url(r'^title/(?P<slug>[\w-]+)/edit/$', views.title_edit, name='title_edit'),

    url(r'^year/$', views.groupby_year, name='group-by-year'),
    url(r'^genre/$', views.groupby_genre, name='group-by-genre'),
    url(r'^director/$', views.groupby_director, name='groupby_director'),

    # CLASS
    url(r'^2year/', views_class.GroupByYearView.as_view()),
    url(r'^2title/(?P<const>tt\d+)/$', views_class.TitleRedirectView.as_view(), name='title-redirect'),
]
