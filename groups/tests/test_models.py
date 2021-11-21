from django.urls import reverse

from MangAdventure.tests.utils import get_test_image

from groups.models import Group, Member, Role

from . import GroupsTestBase


class TestGroup(GroupsTestBase):
    @staticmethod
    def create_group():
        return Group.objects.create(
            name='my group', website='https://test.com/',
            description='My test group', email='scan@test.com',
            id=1, discord='https://discord.gg/abcdefg',
            twitter='MyTwitter', irc='#epicspeedscans',
            reddit='/r/epicspeedscans', logo=get_test_image()
        )

    def setup_method(self):
        super().setup_method()
        self.group = self.create_group()

    def test_create(self):
        assert str(self.group) == 'my group'
        assert str(self.group.logo) == 'groups/1/logo.png'

    def test_get_directory(self):
        assert str(self.group.get_directory()) == 'groups/1'

    def test_get_absolute_url(self):
        assert str(self.group.get_absolute_url()) == reverse(
            'groups:group', kwargs={'g_id': 1}
        )

    def test_members(self):
        assert self.group.members.distinct().count() == 0
        member = TestMember.create_member()
        TestRole.create_role(self.group, member)
        TestRole.create_role(self.group, member, 'TS')
        assert self.group.members.distinct().count() == 1


class TestMember(GroupsTestBase):
    @staticmethod
    def create_member():
        return Member.objects.create(
            name='test', twitter='Whatever',
            discord='Whatever#8150',
            irc='user', reddit='user'
        )

    def setup_method(self):
        super().setup_method()
        self.member = self.create_member()

    def test_create(self):
        assert str(self.member) == 'test'

    def test_groups(self):
        assert self.member.groups.distinct().count() == 0
        group = TestGroup.create_group()
        TestRole.create_role(group, self.member)
        TestRole.create_role(group, self.member, 'TS')
        assert self.member.groups.distinct().count() == 1


class TestRole(GroupsTestBase):
    @staticmethod
    def create_role(group: Group, member: Member, role: str = 'LD'):
        return Role.objects.create(group=group, member=member, role=role)

    def setup_method(self):
        super().setup_method()
        self.member = TestMember.create_member()
        self.group = TestGroup.create_group()

    def test_create(self):
        role = self.create_role(self.group, self.member)
        assert str(role) == 'Leader (my group)'
