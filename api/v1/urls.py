from . import views

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

_series = '^series/(?P<slug>[^/]+)'
_volume = '%s/(?P<vol>[^/]+)' % _series
_authors = '^authors'
_artists = '^artists'
_groups = '^groups'

urlpatterns = [
    url(r'^$', views.invalid_endpoint, name='v1_root'),
    url('^releases/?$', views.all_releases, name='v1_releases'),
    url('^series/?$', views.all_series, name='v1_all_series'),
    url('%s/?$' % _series, views.series, name='v1_series'),
    url('%s/?$' % _volume, views.volume, name='v1_volume'),
    url('%s/(?P<num>[^/]+)/?$' % _volume, views.chapter, name='v1_chapter'),
    url('%s/?$' % _authors, views.all_people, name='v1_all_authors'),
    url('%s/(?P<p_id>[^/]+)/?$' % _authors, views.person, name='v1_author'),
    url('%s/?$' % _artists, views.all_people, name='v1_all_artists'),
    url('%s/(?P<p_id>[^/]+)/?$' % _artists, views.person, name='v1_artist'),
    url('%s/?$' % _groups, views.all_groups, name='v1_all_groups'),
    url('%s/(?P<g_id>[^/]+)/?$' % _groups, views.group, name='v1_group'),
]

