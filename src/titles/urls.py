from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.HomeTemplateView.as_view(), name='home'),
    url(r'^explore/$', views.TitleListView.as_view(), name='title-list'),
    url(r'^title/(?P<imdb_id>tt\d+)/ratings/$', views.RatingUpdateView.as_view(), name='rating-update'),
    url(r'^title/(?P<imdb_id>tt\d+)/(?P<slug>[\w-]*)/$', views.TitleDetailView.as_view(), name='title-detail'),
    url(r'^title/(?P<imdb_id>tt\d+)/$', views.TitleRedirectView.as_view(), name='title-redirect'),

    url(r'^person/(?P<pk>\d+)/(?P<slug>[\w-]*)/$', views.PersonDetailView.as_view(), name='person-detail'),
]
