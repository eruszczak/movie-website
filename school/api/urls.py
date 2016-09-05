from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.test.as_view(), name='test'),
]