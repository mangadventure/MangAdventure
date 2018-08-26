from . import views

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url


app_name = 'api'

_series = '^series/(?P<slug>[^/]+)/'
_volume = '%s(?P<vol>[^/]+)/' % _series
_authors = '^authors/'
_artists = '^artists/'

urlpatterns = [
    url('^$', views.invalid_endpoint, name='invalid'),
    url('^releases/$', views.all_releases, name='releases'),
    url('^series/$', views.all_series, name='series_root'),
    url('%s$' % _series, views.series, name='series'),
    url('%s$' % _volume, views.volume, name='volume'),
    url('%s(?P<num>[^/]+)/$' % _volume, views.chapter, name='chapter'),
    url('%s$' % _authors, views.all_authors, name='author_root'),
    url('%s(?P<auth_id>[^/]+)/$' % _authors, views.author, name='author'),
    url('%s$' % _artists, views.all_artists, name='artist_root'),
    url('%s(?P<art_id>[^/]+)/$' % _artists, views.artist, name='artist'),
]

