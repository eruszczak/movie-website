from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^', include('titles.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^importer/', include('importer.urls')),
    url(r'^', include('shared.urls')),
    url(r'^robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
