from django.conf.urls import include, url
# from users import views

urlpatterns = [
    url(r'^titles/', include('api.title.urls', namespace='api-title')),
    url(r'^ratings/', include('api.rating.urls', namespace='api-rating')),

    # url(r'^school/', include('school.urls')),
    # url(r'^api-school/', include('school.api.urls', namespace='api-school')),
    # url(r'^user-api/', include('school.api.urls')),
]