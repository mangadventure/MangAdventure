from django.urls import path as url
from . import views

app_name = 'api'

_series = 'series/<slug:slug>/'
_volume = '%s<int:vol>/' % _series

urlpatterns = [
    url('releases/', views.all_releases, name='releases'),
    url('series/', views.all_series, name='series_root'),
    url('%s' % _series, views.series, name='series'),
    url('%s' % _volume, views.volume, name='volume'),
    url('%s<int:num>/' % _volume, views.chapter, name='chapter'),
]
