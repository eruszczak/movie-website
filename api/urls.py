from django.conf.urls import include, url

from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'ratings', views.RatingsViewSet)

urlpatterns = [
    url(r'^search', views.SearchAPIView.as_view(), name='search'),
    url(r'^title/(?P<pk>\d+)/rate', views.TitleAddRatingView.as_view(), name='title-rate'),
    url(r'^title/(?P<pk>\d+)/favourites', views.TitleToggleFavourite.as_view(), name='title-fav'),
    url(r'^title/(?P<pk>\d+)/watchlist', views.TitleToggleWatchlist.as_view(), name='title-watch'),
    url(r'^title/(?P<pk>\d+)/recommend', views.RecommendTitle.as_view(), name='title-recommend'),
    url(r'^user/(?P<pk>\d+)/follow', views.FollowUser.as_view(), name='user-follow'),
    url(r'^user/(?P<pk>\d+)/favourites/reorder', views.ReorderFavourite.as_view(), name='user-fav-reorder'),

    url(r'^', include(router.urls), name='ratings'),
    url(r'^title/(?P<slug>[\w-]+)/$', views.TitleDetailView.as_view(), name='title_detail'),
]
