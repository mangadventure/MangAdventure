"""The main URLconf of the api app."""

from django.urls import include, path

#: The URL namespace of the API app.
app_name = 'api'

#: The main URL patterns of the API app.
urlpatterns = [
    path('v1/', include('api.v1.urls')),
    path('v2/', include('api.v2.urls')),
]

__all__ = ['urlpatterns']
