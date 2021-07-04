"""The URLconf of the api.v2 app."""

from django.urls import include, path

from rest_framework.routers import SimpleRouter

from users import api as users_api

from .views import openapi, redoc_redirect, swagger_redirect

#: The API router
router = SimpleRouter()
router.register('bookmarks', users_api.BookmarkViewSet, 'bookmarks')
router.register('token', users_api.ApiKeyViewSet, 'token')

#: The URL namespace of the api.v2 app.
app_name = 'v2'

#: The URL patterns of the api.v2 app.
urlpatterns = [
    path('', include(router.urls)),
    # HACK: move profile operations to the main endpoint
    path('profile/', users_api.ProfileViewSet.as_view()),
    path('openapi.json', openapi, name='schema'),
    path('redoc/', redoc_redirect, name='redoc'),
    path('swagger/', swagger_redirect, name='swagger'),
]

__all__ = ['app_name', 'urlpatterns']
