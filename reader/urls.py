"""The URLconf of the reader app."""

from django.urls import path, register_converter

from MangAdventure.utils.converters import FloatConverter

from . import views

register_converter(FloatConverter, 'float')

#: The URL namespace of the reader app.
app_name = 'reader'

_slug = '<slug:slug>/'
_chapter = f'{_slug}<int:vol>/<float:num>/'
_page = f'{_chapter}<int:page>/'

#: The URL namespace of the reader app.
urlpatterns = [
    path('', views.directory, name='directory'),
    path(_slug, views.series, name='series'),
    path(_chapter, views.chapter_redirect, name='chapter'),
    path(_page, views.chapter_page, name='page'),
    # path(f'{_chapter}comments/', views.chapter_comments, name='comments'),
]

__all__ = ['app_name', 'urlpatterns']
