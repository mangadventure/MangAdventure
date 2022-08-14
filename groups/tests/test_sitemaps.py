from groups.models import Group
from groups.sitemaps import GroupSitemap

from . import GroupsTestBase


class TestSitemaps(GroupsTestBase):
    def setup_method(self):
        super().setup_method()
        self.group = Group.objects.create(name='Group')

    def test_groups(self):
        sitemap = GroupSitemap()
        assert list(sitemap.items()) == [self.group]
        assert self.group.sitemap_images == []
