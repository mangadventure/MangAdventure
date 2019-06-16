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

app_name = 'api:v1'

urlpatterns = [
    url(r'^$', views.invalid_endpoint, name='root'),
    url('^releases/?$', views.all_releases, name='releases'),
    url('^series/?$', views.all_series, name='all_series'),
    url('%s/?$' % _series, views.series, name='series'),
    url('%s/?$' % _volume, views.volume, name='volume'),
    url('%s/(?P<num>[^/]+)/?$' % _volume, views.chapter, name='chapter'),
    url('%s/?$' % _authors, views.all_people, name='all_authors'),
    url('%s/(?P<p_id>[^/]+)/?$' % _authors, views.person, name='author'),
    url('%s/?$' % _artists, views.all_people, name='all_artists'),
    url('%s/(?P<p_id>[^/]+)/?$' % _artists, views.person, name='artist'),
    url('%s/?$' % _groups, views.all_groups, name='all_groups'),
    url('%s/(?P<g_id>[^/]+)/?$' % _groups, views.group, name='group'),
    url('^categories/?$', views.categories, name='categories'),
]
