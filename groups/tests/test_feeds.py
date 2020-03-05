from django.http import HttpRequest
from django.utils.feedgenerator import Atom1Feed

from groups.feeds import GroupAtom, GroupRSS
from groups.models import Group
from reader.models import Chapter, Series

from . import GroupsTestBase


class TestGroup(GroupsTestBase):
    def _test_feed(self, feed):
        if feed.feed_type is Atom1Feed:
            description = feed.subtitle
        else:
            description = feed.description
        assert feed.author_name == 'MangAdventure'
        assert feed.title(self.group) == 'Group - MangAdventure'
        assert feed.link(self.group) == self.group.get_absolute_url()
        assert description(self.group) == \
            'Updates when a new chapter is added by Group'
        assert list(feed.items(self.group)) == [self.chapter]
        assert str(self.chapter) in feed.item_description(self.chapter)
        assert feed.item_title(self.chapter) == str(self.chapter)
        assert feed.item_pubdate(self.chapter) == self.chapter.published
        assert feed.item_updateddate(self.chapter) == self.chapter.modified

    def setup_method(self):
        super().setup_method()
        self.request = HttpRequest()
        self.group = Group.objects.create(name='Group')
        self.series = Series.objects.create(title='Series')
        self.chapter = Chapter.objects.create(
            title='Chapter', number=1.0, series=self.series
        )
        self.chapter.groups.add(self.group)

    def test_atom(self):
        feed = GroupAtom()
        self._test_feed(feed)
        r = feed(self.request, self.group.id)
        date = self.chapter.modified.isoformat()
        assert f'<updated>{date}' in str(r.content)

    def test_rss(self):
        feed = GroupRSS()
        self._test_feed(feed)
        r = feed(self.request, self.group.id)
        assert '<guid isPermaLink="true"' in str(r.content)
