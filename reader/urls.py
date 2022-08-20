"""The URLconf of the reader app."""

from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import path, register_converter
from django.views.decorators.cache import cache_control

from MangAdventure.converters import FloatConverter

from . import feeds, sitemaps, views

register_converter(FloatConverter, 'float')

#: The URL namespace of the reader app.
app_name = 'reader'

_slug = '<slug:slug>/'
_chapter = f'{_slug}<int:vol>/<float:num>/'
_page = f'{_chapter}<int:page>/'

_sitemaps = {
    'template_name': 'image-sitemap.xml',
    'sitemaps': {
        'series': sitemaps.SeriesSitemap,
        'chapters': sitemaps.ChapterSitemap
    }
}

_sitemap = cache_control(max_age=86400, must_revalidate=True)(sitemap)

#: The URL namespace of the reader app.
urlpatterns = [
    path('', views.directory, name='directory'),
    path(_slug, views.series, name='series'),
    path(_chapter, views.chapter_redirect, name='chapter'),
    path(_page, views.chapter_page, name='page'),
    path(f'{_slug[:-1]}.atom', feeds.ReleasesAtom(), name='series.atom'),
    path(f'{_slug[:-1]}.rss', feeds.ReleasesRSS(), name='series.rss'),
    path('<section>-sitemap.xml', _sitemap, _sitemaps, name='sitemap.xml'),
]

if settings.CONFIG['ALLOW_DLS']:
    urlpatterns.append(
        path(f'{_chapter[:-1]}.cbz', views.chapter_download, name='cbz')
    )

__all__ = ['app_name', 'urlpatterns']
