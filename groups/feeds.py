from typing import TYPE_CHECKING, Iterable

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from reader.models import Chapter

from .models import Group

if TYPE_CHECKING:
    from datetime import datetime
    from django.http import HttpRequest


class GroupRSS(Feed):
    """RSS feed for a group's releases."""
    ttl = 600
    author_name = settings.CONFIG['NAME']
    item_guid_is_permalink = True

    def get_object(self, request: 'HttpRequest', g_id: int) -> Group:
        """
        Get a ``Group`` object from the request.

        :param request: The original request.
        :param g_id: The id of the group.

        :return: The group that has the given id.
        """
        return Group.objects.prefetch_related('releases').get(id=g_id)

    def link(self, obj: Group) -> str:
        """
        Get the link of the feed's page.

        :param obj: The object of the feed.

        :return: The URL of the group.
        """
        return obj.get_absolute_url()

    def title(self, obj: Group) -> str:
        """
        Get the title of the feed.

        :param obj: The object of the feed.

        :return: The name of the group.
        """
        return f'{obj.name} - {self.author_name}'

    def description(self, obj: Group) -> str:
        """
        Get the description of the feed.

        :param obj: The object of the feed.

        :return: A description with the name of the group.
        """
        return f'Updates when a new chapter is added by {obj.name}'

    def items(self, obj: Group) -> Iterable[Chapter]:
        """
        Get an iterable of the feed's items.

        :param obj: The object of the feed.

        :return: An iterable of ``Chapter`` objects.
        """
        _max = settings.CONFIG['MAX_RELEASES']
        return obj.releases.order_by('-uploaded')[:_max]

    def item_description(self, item: Chapter) -> str:
        """
        Get the description of the item.

        :param item: A ``Chapter`` object.

        :return: The ``Chapter`` object as a string.
        """
        desc = str(item)
        if settings.CONFIG['ALLOW_DLS']:
            domain = settings.CONFIG["DOMAIN"]
            url = item.get_absolute_url()[:-1] + '.cbz'
            desc = f'<a href="http://{domain}{url}">{desc}</a>'
        return desc

    def item_pubdate(self, item: Chapter) -> 'datetime':
        """
        Get the publication date of the item.

        :param item: A ``Chapter`` object.

        :return: The date the chapter was uploaded.
        """
        return item.uploaded

    def item_updateddate(self, item: Chapter) -> 'datetime':
        """
        Get the update date of the item.

        :param item: A ``Chapter`` object.

        :return: The date the chapter was modified.
        """
        return item.modified


class GroupAtom(GroupRSS):
    """Atom feed for a group's releases."""
    feed_type = Atom1Feed
    subtitle = GroupRSS.description


__all__ = ['GroupRSS', 'GroupAtom']
