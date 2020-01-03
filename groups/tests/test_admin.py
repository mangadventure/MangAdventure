from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest

from MangAdventure.tests import get_test_image

from groups.admin import GroupAdmin, MemberAdmin
from groups.models import Group, Member

from . import GroupsTestBase


class GroupsAdminTestBase(GroupsTestBase):
    def setup_method(self):
        self.site = AdminSite()
        self.request = HttpRequest()


class TestMemberAdmin(GroupsAdminTestBase):
    def setup_method(self):
        super().setup_method()
        self.admin = MemberAdmin(admin_site=self.site, model=Member)
        self.member = Member.objects.create(name='name')

    def test_twitter_empty(self):
        assert self.admin._twitter(self.member) == ''

    def test_twitter(self):
        self.member.twitter = "Test"
        self.member.save()
        twitter_url = 'https://twitter.com'
        assert self.admin._twitter(self.member)\
            .startswith(f'<a href="{twitter_url}/{self.member.twitter}"')

    def test_reddit_empty(self):
        assert self.admin._reddit(self.member) == ''

    def test_reddit(self):
        self.member.reddit = 'user'
        self.member.save()
        reddit_url = 'https://reddit.com/u'
        assert self.admin._reddit(self.member)\
            .startswith(f'<a href="{reddit_url}/{self.member.reddit}"')


class TestGroupAdmin(GroupsAdminTestBase):
    def setup_method(self):
        super().setup_method()
        self.admin = GroupAdmin(admin_site=self.site, model=Group)
        self.group = Group.objects.create(name='test', logo=get_test_image())

    def test_image(self):
        assert self.admin.image(self.group)\
            .startswith('<img src="')

    def test_image_empty(self):
        self.group.logo = None
        self.group.save()
        assert self.admin.image(self.group) == ''

    def test_website_empty(self):
        assert self.admin._website(self.group) == ''

    def test_website(self):
        self.group.website = 'https://site.com'
        self.group.save()
        assert self.admin._website(self.group)\
            .startswith(f'<a href="{self.group.website}"')
