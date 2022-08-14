"""Sitemaps for the groups app."""

from typing import Iterable

from django.contrib.sitemaps import Sitemap

from .models import Group


class GroupSitemap(Sitemap):
    """Sitemap for groups."""
    #: The priority of the sitemap.
    priority = 0.4

    def items(self) -> Iterable[Group]:
        """
        Get an iterable of the sitemap's items.

        :return: An iterable of ``Group`` objects.
        """
        return Group.objects.only('name', 'logo').order_by('name')


__all__ = ['GroupSitemap']
