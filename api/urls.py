from .v1.views import invalid_endpoint

try:
    from django.urls import include, re_path as url
except ImportError:
    from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', invalid_endpoint, name='root'),
    url(r'^v1/', include('api.v1.urls')),
]

