from django.conf.urls import include, url

from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'ratings', views.RatingsViewSet)

urlpatterns = [
    url(r'^search', views.SearchAPIView.as_view(), name='search'),
    url(r'^title/(?P<pk>\d+)/rate', views.AddRatingAPIView.as_view(), name='title-rate'),
    url(r'^title/(?P<pk>\d+)/favourites', views.ToggleFavouriteAPIView.as_view(), name='title-fav'),
    url(r'^title/(?P<pk>\d+)/watchlist', views.ToggleWatchlistAPIView.as_view(), name='title-watch'),
    url(r'^title/(?P<pk>\d+)/recommend', views.RecommendTitleAPIView.as_view(), name='title-recommend'),
    url(r'^tv/(?P<pk>\d+)/watching', views.ToggleCurrentlyWatchingTV.as_view(), name='tv-watching'),
    url(r'^user/(?P<pk>\d+)/follow', views.ToggleFollowUser.as_view(), name='user-follow'),
    url(r'^user/(?P<pk>\d+)/favourites/reorder', views.ReorderFavourite.as_view(), name='user-fav-reorder'),
    url(r'^user/(?P<pk>\d+)/export/$', views.ExportRatingsAPIView.as_view(), name='user-export-ratings'),
    url(r'^user/(?P<pk>\d+)/import/$', views.ImportRatingsAPIView.as_view(), name='user-import-ratings'),

    url(r'^', include(router.urls), name='ratings'),
    url(r'^title/(?P<slug>[\w-]+)/$', views.TitleDetailView.as_view(), name='title_detail'),
]
