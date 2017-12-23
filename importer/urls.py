from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^user/(?P<pk>\d+)/export', importer.views.ExportRatingsAPIView.as_view(), name='user-export-ratings'),
    url(r'^(?P<username>[-\w]+)/import', view.ImportRatingsAPIView.as_view(), name='user-import-ratings'),
]
