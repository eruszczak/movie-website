from django.conf.urls import include, url
# from users import views

urlpatterns = [
    url(r'^titles/', include('api.title.urls', namespace='api-title')),
    url(r'^ratings/', include('api.rating.urls', namespace='api-rating')),

]