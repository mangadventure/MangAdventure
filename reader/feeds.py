from mimetypes import guess_type
from typing import TYPE_CHECKING, Iterable

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from .models import Series

if TYPE_CHECKING:
    from datetime import datetime


class LibraryRSS(Feed):
    """RSS feed for the series library."""
    #: The TTL of the feed.
    ttl = 600
    #: The link of the feed.
    link = '/reader/'
    #: The title of the feed.
    title = 'Library feed'
    #: The description of the feed.
    description = 'Updates when a new series is added'
    #: The name of the site.
    author_name = settings.CONFIG['NAME']
    #: The GUID of items is a link.
    item_guid_is_permalink = True

    def items(self) -> Iterable[Series]:
        """
        Get an iterable of the feed's items.

        :return: An iterable of ``Series``.
        """
        _max = settings.CONFIG['MAX_RELEASES']
        return Series.objects.order_by('-created')[:_max]

    def item_title(self, item: Series) -> str:
        """
        Get the title of the item.

        :param item: A ``Series`` object.

        :return: The title of the series.
        """
        return item.title

    def item_description(self, item: Series) -> str:
        """
        Get the description of the item.

        :param item: A ``Series`` object.

        :return: The description of the series.
        """
        return item.description.replace('\n', '<br/>')

    def item_categories(self, item: Series) -> Iterable[str]:
        """
        Get the categories of the item.

        :param item: A ``Series`` object.

        :return: The names of the series' categories.
        """
        return item.categories.values_list('name', flat=True)

    def item_enclosure_url(self, item: Series) -> str:
        """
        Get the enclosure URL of the item.

        :param item: A ``Series`` object.

        :return: The URL of the series' cover image.
        """
        url = item.cover.url
        if url[:4] == 'http':
            return url
        return f'http://{settings.CONFIG["DOMAIN"]}{url}'

    def item_enclosure_length(self, item: Series) -> int:
        """
        Get the enclosure length of the item.

        :param item: A ``Series`` object.

        :return: The size of the series' cover image.
        """
        return item.cover.size

    def item_enclosure_mime_type(self, item: Series) -> str:
        """
        Get the enclosure type of the item.

        :param item: A ``Series`` object.

        :return: The mime type of the series' cover image.
        """
        return guess_type(item.cover.path)[0]

    def item_pubdate(self, item: Series) -> 'datetime':
        """
        Get the publication date of the item.

        :param item: A ``Series`` object.

        :return: The date the series was created.
        """
        return item.created

    def item_updateddate(self, item: Series) -> 'datetime':
        """
        Get the update date of the item.

        :param item: A ``Series`` object.

        :return: The date the series was modified.
        """
        return item.modified


class LibraryAtom(LibraryRSS):
    """Atom feed for the series library."""
    #: The type of the feed.
    feed_type = Atom1Feed
    #: The subtitle of the feed.
    subtitle = LibraryRSS.description
