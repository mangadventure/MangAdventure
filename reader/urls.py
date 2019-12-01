from . import views

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

app_name = 'reader'

_slug = '^(?P<slug>[A-Za-z0-9_-]+)'
_chapter = '%s/(?P<vol>[0-9]+)/(?P<num>[0-9]+([.][0-9]+|))' % _slug
_page = '%s/(?P<page>[0-9]+)' % _chapter

urlpatterns = [
    url('^$', views.directory, name='directory'),
    url('%s/$' % _slug, views.series, name='series'),
    url('%s/$' % _chapter, views.chapter_redirect, name='chapter'),
    url('%s/$' % _page, views.chapter_page, name='page'),
    # url('%s/comments/$' % _chapter, views.chapter_comments, name='comments'),
]
