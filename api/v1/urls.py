"""The URLconf of the api.v1 app."""

from django.urls import path, register_converter

from MangAdventure.converters import FloatConverter

from . import views

register_converter(FloatConverter, 'float')

_series = 'series/<slug:slug>'
_volume = f'{_series}/<int:vol>'
_authors = 'authors'
_artists = 'artists'
_groups = 'groups'

#: The URL namespace of the api.v1 app.
app_name = 'v1'

#: The URL patterns of the api.v1 app.
urlpatterns = [
    path('', views.invalid_endpoint, name='root'),
    path('releases/', views.all_releases, name='releases'),
    path('series/', views.all_series, name='all_series'),
    path(f'{_series}/', views.series, name='series'),
    path(f'{_volume}/', views.volume, name='volume'),
    path(f'{_volume}/<float:num>/', views.chapter, name='chapter'),
    path(f'{_authors}/', views.all_people, name='all_authors'),
    path(f'{_authors}/<int:p_id>/', views.person, name='author'),
    path(f'{_artists}/', views.all_people, name='all_artists'),
    path(f'{_artists}/<int:p_id>/', views.person, name='artist'),
    path(f'{_groups}/', views.all_groups, name='all_groups'),
    path(f'{_groups}/<int:g_id>/', views.group, name='group'),
    path('categories/', views.categories, name='categories'),
]

__all__ = ['app_name', 'urlpatterns']
