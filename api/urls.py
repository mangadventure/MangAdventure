"""The main URLconf of the api app."""

from django.urls import include, path

from .v1.views import invalid_endpoint

#: The URL namespace of the API app.
app_name = "api"

#: The main URL patterns of the API app.
urlpatterns = [
    path('', invalid_endpoint, name='root'),
    path('v1/', include('api.v1.urls')),
]

__all__ = ['urlpatterns']
