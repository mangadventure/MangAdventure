from pytest import mark

from groups.models import Group, Member, Role
from groups.templatetags.group_tags import group_roles


@mark.django_db
def test_group_roles():
    group = Group.objects.create(name='test')
    member = Member.objects.create(name='member')
    Role.objects.create(group=group, member=member, role='LD')
    assert group_roles(member, group) == 'Leader'
