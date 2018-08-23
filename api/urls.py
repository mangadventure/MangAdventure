from . import views

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url


app_name = 'api'

_series = '^series/(?P<slug>[\w_-]+)/'
_volume = '%s(?P<vol>\d+)/' % _series

urlpatterns = [
    url('^$', views.invalid_endpoint, name='invalid'),
    url('^releases/$', views.all_releases, name='releases'),
    url('^series/$', views.all_series, name='series_root'),
    url('%s$' % _series, views.series, name='series'),
    url('%s$' % _volume, views.volume, name='volume'),
    url('%s(?P<num>\d+)/$' % _volume, views.chapter, name='chapter'),
]
