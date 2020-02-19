from typing import TYPE_CHECKING, Iterable

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.db.models.expressions import Subquery
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers
from django.utils.http import http_date
from django.utils.feedgenerator import Atom1Feed

from reader.models import Chapter

if TYPE_CHECKING:
    from datetime import datetime
    from django.http import HttpRequest


class BookmarksRSS(Feed):
    """RSS feed for a user's bookmarks."""
    ttl = 600
    link = '/user/'
    author_name = settings.CONFIG['NAME']
    title = f'Bookmarks - {author_name}'
    description = 'Updates when a bookmarked series has a new release'
    item_guid_is_permalink = True

    def __call__(self, request: 'HttpRequest', *args, **kwargs) -> HttpResponse:
        """
        Get the HTTP response of the feed.

        :param request: The original request.

        :return: | A :status:`401` response if the token is missing.
                 | A :status:`403` response if the provided token is invalid.
                 | A :status:`200` response with the bookmarks feed otherwise.
        """
        token = request.GET.get('token')
        if not token:
            header = request.META.get('HTTP_AUTHORIZATION')
            if not header:
                res = HttpResponse(
                    b'A token is required to access the feed.',
                    status=401, content_type='text/plain'
                )
                res['WWW-Authenticate'] = 'Bearer realm="bookmarks feed"'
                return res
            if header[:7] != 'Bearer ':
                return HttpResponse(
                    b'Authorization header format is invalid.',
                    status=403, content='text/plain'
                )
            token = header[7:]
        try:
            obj = User.objects.get(profile__token=token)
        except User.DoesNotExist:
            return HttpResponse(
                b'The provided token is invalid.',
                status=403, content_type='text/plain'
            )
        feedgen = self.get_feed(obj, request)
        res = HttpResponse(content_type=feedgen.content_type)
        patch_vary_headers(res, ('Authorization',))
        res['Last-Modified'] = http_date(
            feedgen.latest_post_date().timestamp()
        )
        feedgen.write(res, 'utf-8')
        return res

    def items(self, obj: User) -> Iterable[Chapter]:
        """
        Get an iterable of the feed's items.

        :param obj: The object of the feed.

        :return: An iterable of ``Chapter`` objects.
        """
        return Chapter.objects.filter(id__in=Subquery(
            obj.bookmarks.values('series__chapters')
        )).select_related('series').order_by('-uploaded')

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


class BookmarksAtom(BookmarksRSS):
    """Atom feed for a user's bookmarks."""
    feed_type = Atom1Feed
    subtitle = BookmarksRSS.description


__all__ = ['BookmarksRSS', 'BookmarksAtom']
