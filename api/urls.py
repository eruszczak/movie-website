from django.conf.urls import include, url

from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'ratings', views.RatingsViewSet)

urlpatterns = [
    url(r'^title/(?P<pk>\d+)/rate', views.TitleAddRatingView.as_view(), name='title-rate'),
    url(r'^title/(?P<pk>\d+)/favourites', views.TitleToggleFavourite.as_view(), name='title-fav'),
    url(r'^title/(?P<pk>\d+)/watchlist', views.TitleToggleWatchlist.as_view(), name='title-watch'),
    url(r'^user/(?P<pk>\d+)/follow', views.UserToggleFavourite.as_view(), name='user-follow'),
    url(r'^user/(?P<pk>\d+)/favourites/reorder', views.ReorderFavourite.as_view(), name='user-fav-reorder'),

    url(r'^', include(router.urls), name='ratings'),
    url(r'^g/$', views.Genres.as_view(), name='genres'),
    url(r'^y/$', views.Years.as_view(), name='years'),
    url(r'^r/$', views.Rates.as_view(), name='rates'),
    url(r'^m/$', views.MonthlyRatings.as_view(), name='monthly'),
    url(r'^title/(?P<slug>[\w-]+)/$', views.TitleDetailView.as_view(), name='title_detail'),
]
