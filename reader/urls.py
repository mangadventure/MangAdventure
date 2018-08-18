from django.urls import path as url
from . import views

app_name = 'reader'

_slug = 'reader/<slug:slug>/'
_chapter = '%s<int:vol>/<int:num>/' % _slug

urlpatterns = [
    url('', views.index, name='index'),
    url('reader/', views.directory, name='directory'),
    url('%s' % _slug, views.series, name='series'),
    url('%s' % _chapter, views.chapter_redirect, name='chapter'),
    url('%s<int:page>/' % _chapter, views.chapter, name='chapter'),
]

