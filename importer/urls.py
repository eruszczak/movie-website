from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^user/(?P<pk>\d+)/export', views.ExportRatingsAPIView.as_view(), name='user-export-ratings'),
    url(r'^import', views.ImportRatingsFormView.as_view(), name='user-import-ratings'),
]
