"""The URLconf of the api.v1 app."""

from django.http import HttpResponseGone
from django.urls import path, register_converter

from MangAdventure.converters import FloatConverter

register_converter(FloatConverter, 'float')

_series = 'series/<slug:slug>'
_volume = f'{_series}/<int:vol>'
_authors = 'authors'
_artists = 'artists'
_groups = 'groups'

#: The URL namespace of the api.v1 app.
app_name = 'v1'

def _gone(*args, **kwargs) -> HttpResponseGone:
    return HttpResponseGone('Use API v2 instead.')

#: The URL patterns of the api.v1 app.
urlpatterns = [
    path('releases/', _gone, name='releases'),
    path('series/', _gone, name='all_series'),
    path(f'{_series}/', _gone, name='series'),
    path(f'{_volume}/', _gone, name='volume'),
    path(f'{_volume}/<float:num>/', _gone, name='chapter'),
    path(f'{_authors}/', _gone, name='all_authors'),
    path(f'{_authors}/<int:p_id>/', _gone, name='author'),
    path(f'{_artists}/', _gone, name='all_artists'),
    path(f'{_artists}/<int:p_id>/', _gone, name='artist'),
    path(f'{_groups}/', _gone, name='all_groups'),
    path(f'{_groups}/<int:g_id>/', _gone, name='group'),
    path('categories/', _gone, name='categories'),
]

__all__ = ['app_name', 'urlpatterns']
