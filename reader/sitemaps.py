"""Sitemaps for the reader app."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from django.contrib.sitemaps import Sitemap
from django.db.models import Prefetch

from .models import Chapter, Page, Series

if TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime  # isort:skip


class SeriesSitemap(Sitemap):
    """Sitemap for series."""
    #: The priority of the sitemap.
    priority = 0.7

    #: The change frequency of the items.
    changefreq = 'weekly'

    def items(self) -> Iterable[Series]:
        """
        Get an iterable of the sitemap's items.

        :return: An iterable of ``Series`` objects.
        """
        return Series.objects.only('cover', 'modified').order_by('modified')

    def lastmod(self, item: Series) -> datetime:
        """
        Get the last modified date of the item.

        :param item: A ``Series`` object.

        :return: The date the series was modified.
        """
        return item.modified


class ChapterSitemap(Sitemap):
    """Sitemap for chapters."""
    #: The priority of the sitemap.
    priority = 0.6

    #: The change frequency of the items.
    changefreq = 'never'

    #: The maximum number of items allowed.
    limit = 1000

    def items(self) -> Iterable[Chapter]:
        """
        Get an iterable of the sitemap's items.

        :return: An iterable of ``Chapter`` objects.
        """
        return Chapter.objects.prefetch_related(
            Prefetch('pages', queryset=Page.objects.order_by('number'))
        ).only('modified').order_by('modified')

    def lastmod(self, item: Chapter) -> datetime:
        """
        Get the last modified date of the item.

        :param item: A ``Series`` object.

        :return: The date the chapter was modified.
        """
        return item.modified


__all__ = ['SeriesSitemap', 'ChapterSitemap']
