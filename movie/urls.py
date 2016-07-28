from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^explore/$', views.explore, name='explore'),
    url(r'^about/$', views.about, name='about'),

    # url(r'^(?P<const>tt\d{7})/$', views.entry_details, name='entry_details'),
    url(r'^title/(?P<slug>[\w-]+)/$', views.entry_details, name='entry_details'),

    url(r'^year/$', views.entry_groupby_year, name='entry_groupby_year'),
    url(r'^year/(?P<year>\d{4})/$', views.entry_show_from_year, name='entry_show_from_year'),

    # url(r'^(?P<year>\d{4})/(?P<month>\d\d*)/$', views.entry_show_rated_in_month, name='entry_show_rated_in_month'),
    url(r'^(?P<year>201[3-9])/(?P<month>0*[1-9]|1[0-2])/$', views.entry_show_rated_in_month, name='entry_show_rated_in_month'),

    url(r'^genre/$', views.entry_groupby_genre, name='entry_groupby_genre'),
    url(r'^genre/(?P<genre>\S+)/$', views.entry_show_from_genre, name='entry_show_from_genre'),

    url(r'^rated/(?P<rate>\d+)/$', views.entry_show_from_rate, name='entry_show_from_rate'),
]
