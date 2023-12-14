"""Miscellaneous sitemaps."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class MiscSitemap(Sitemap):
    """Sitemap for miscellaneous pages."""

    def items(self) -> tuple[str, ...]:
        """
        Get a tuple of the sitemap's items.

        :return: A tuple of page names.
        """
        return ('index', 'search', 'reader:directory', 'info', 'privacy')

    def location(self, item: str) -> str:
        """
        Get the location of the item.

        :param item: A page name.

        :return: The URL of the page.
        """
        return reverse(item)

    def priority(self, item: str) -> float:
        """
        Get the priority of the item.

        :param item: A page name.

        :return: The priority of the page.
        """
        return 0.8 if self._is_reader(item) else 0.5

    def changefreq(self, item: str) -> str:
        """
        Get the change frequency of the item.

        :param item: A page name.

        :return: The change frequency of the page.
        """
        return 'daily' if self._is_reader(item) else 'never'

    @staticmethod
    def _is_reader(item: str) -> bool:
        return item == 'index' or item == 'reader:directory'


__all__ = ['MiscSitemap']
