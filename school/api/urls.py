from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.GetResponse.as_view(), name='test'),
]