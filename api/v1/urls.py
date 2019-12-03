from . import views

from django.urls import path as url

_series = 'series/<slug:slug>'
_volume = f'{_series}/<int:vol>'
_authors = 'authors'
_artists = 'artists'
_groups = 'groups'

app_name = 'api:v1'

urlpatterns = [
    url('', views.invalid_endpoint, name='root'),
    url('releases/', views.all_releases, name='releases'),
    url('series/', views.all_series, name='all_series'),
    url(f'{_series}/', views.series, name='series'),
    url(f'{_volume}/', views.volume, name='volume'),
    url(f'{_volume}/<float:num>/', views.chapter, name='chapter'),
    url(f'{_authors}/', views.all_people, name='all_authors'),
    url(f'{_authors}/<int:p_id>/', views.person, name='author'),
    url(f'{_artists}/', views.all_people, name='all_artists'),
    url(f'{_artists}/<int:p_id>/', views.person, name='artist'),
    url(f'{_groups}/', views.all_groups, name='all_groups'),
    url(f'{_groups}/<int:g_id>/', views.group, name='group'),
    url('categories/', views.categories, name='categories'),
]
