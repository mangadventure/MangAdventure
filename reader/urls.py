from . import views

from django.urls import path as url

app_name = 'reader'

_slug = '<slug:slug>/'
_chapter = f'{_slug}<int:vol>/<float:num>/'
_page = f'{_chapter}<int:page>/'

urlpatterns = [
    url('', views.directory, name='directory'),
    url(_slug, views.series, name='series'),
    url(_chapter, views.chapter_redirect, name='chapter'),
    url(_page, views.chapter_page, name='page'),
    # url(f'{_chapter}comments/', views.chapter_comments, name='comments'),
]
