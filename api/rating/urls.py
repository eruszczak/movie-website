from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.RatingListView.as_view(), name='rating_list'),
    url(r'^g/$', views.Genres.as_view(), name='genres'),
    url(r'^y/$', views.Years.as_view(), name='years'),
    url(r'^r/$', views.Rates.as_view(), name='rates'),
    url(r'^m/$', views.MonthlyRatings.as_view(), name='monthly'),
]