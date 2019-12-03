from .v1.views import invalid_endpoint

from django.urls import include, path as url

urlpatterns = [
    url('', invalid_endpoint, name='root'),
    url('v1/', include('api.v1.urls')),
]
