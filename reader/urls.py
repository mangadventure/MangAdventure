from . import views

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

app_name = 'reader'

_slug = '^(?P<slug>[A-Za-z0-9_-]+)/'
_chapter = '%s(?P<vol>[0-9]+)/(?P<num>[0-9]+([.][0-9]+|))/' % _slug
_page = '%s(?P<page>[0-9]+)/' % _chapter

urlpatterns = [
    url(r'^$', views.directory, name='directory'),
    url(r'%s$' % _slug, views.series, name='series'),
    url(r'%s$' % _chapter, views.chapter_redirect, name='chapter'),
    url(r'%s$' % _page, views.chapter_page, name='page'),
]
