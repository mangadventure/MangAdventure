from django.urls import reverse

from groups.models import Group, Member, Role

from . import GroupsTestBase


class TestAllGroups(GroupsTestBase):
    URL = reverse('groups:all_groups')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200


class TestGroup(GroupsTestBase):
    def setup_method(self):
        super().setup_method()
        self.group = Group.objects.create(name='test')
        self.member = Member.objects.create(name='member')
        Role.objects.create(group=self.group, member=self.member, role='LD')

    def test_get(self):
        r = self.client.get(reverse(
            'groups:group', kwargs={'g_id': self.group.id}
        ))
        assert self.group.id == 1
        assert r.status_code == 200

    def test_get_not_found(self):
        r = self.client.get(reverse('groups:group', kwargs={'g_id': 3}))
        assert r.status_code == 404

    def test_get_zero(self):
        r = self.client.get(reverse('groups:group', kwargs={'g_id': 0}))
        assert r.status_code == 404
