from django.http import HttpRequest
from django.utils.feedgenerator import Atom1Feed

from reader.models import Chapter, Series
from users.feeds import BookmarksAtom, BookmarksRSS
from users.models import User, UserProfile

from . import UsersTestBase


class TestBookmarks(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.request = HttpRequest()
        self.chapter1 = Chapter.objects.create(
            title='Chapter1', number=1.0, series=self.series
        )
        self.series2 = Series.objects.get(pk=2)
        self.chapter2 = Chapter.objects.create(
            title='Chapter2', number=1.0, series=self.series2
        )
        self.user2 = User.objects.get(pk=2)
        self.user.bookmarks.create(series=self.series)
        self.user2.bookmarks.create(series=self.series2)
        UserProfile.objects.get_or_create(user_id=1)
        UserProfile.objects.get_or_create(user_id=2)

    def _test_feed(self, feed, chapter):
        assert feed.link == '/user/'
        assert feed.author_name == 'MangAdventure'
        assert feed.title == 'Bookmarks - MangAdventure'
        desc = 'Updates when a bookmarked series has a new release'
        if feed.feed_type is Atom1Feed:
            assert feed.subtitle == desc
        else:
            assert feed.description == desc
        assert feed.item_title(chapter) == str(chapter)
        assert str(chapter) in feed.item_description(chapter)
        assert feed.item_pubdate(chapter) == chapter.published
        assert feed.item_updateddate(chapter) == chapter.modified

    def test_atom(self):
        feed = BookmarksAtom()
        self._test_feed(feed, self.chapter1)
        assert list(feed.items(self.user)) == [self.chapter1]
        self.request.GET['token'] = self.user.profile.token
        r = feed(self.request)
        date = self.chapter1.modified.isoformat()
        assert f'<updated>{date}' in str(r.content)
        assert 'Authorization' in r['Vary']

    def test_rss(self):
        feed = BookmarksRSS()
        self._test_feed(feed, self.chapter2)
        assert list(feed.items(self.user2)) == [self.chapter2]
        self.request.META['HTTP_AUTHORIZATION'] = \
            f'Bearer {self.user2.profile.token}'
        r = feed(self.request)
        assert '<guid isPermaLink="true"' in str(r.content)
        assert 'Authorization' in r['Vary']

    def test_invalid(self):
        feed = BookmarksRSS()
        r = feed(self.request)
        assert r.status_code == 401
        assert 'token is required' in str(r.content)
        assert r['WWW-Authenticate'] == \
            'Bearer realm="bookmarks feed", charset="utf-8"'

        self.request.META['HTTP_AUTHORIZATION'] = 'Invalid'
        r = feed(self.request)
        assert r.status_code == 403
        assert 'header format is invalid' in str(r.content)

        self.request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid'
        r = feed(self.request)
        assert r.status_code == 403
        assert 'token is invalid' in str(r.content)
