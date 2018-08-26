from . import views
try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

app_name = 'reader'

_slug = '^(?P<slug>[\w\d_-]+)/'
_chapter = '%s(?P<vol>\d+)/(?P<num>\d+)/' % _slug

urlpatterns = [
    url(r'^$', views.directory, name='directory'),
    url(r'%s$' % _slug, views.series, name='series'),
    url(r'%s$' % _chapter, views.chapter_redirect, name='chapter'),
    url(r'%s(?P<page>\d+)/$' % _chapter, views.chapter, name='chapter'),
]

