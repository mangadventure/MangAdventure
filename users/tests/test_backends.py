from django.contrib.auth.models import User

from . import UsersTestBase


class TestScanlationBackend(UsersTestBase):
    def test_scanlator(self):
        user = User.objects.get(pk=2)
        assert user.has_perm('edit', self.series)

    def test_inactive(self):
        user = User.objects.get(pk=2)
        user.is_active = False
        assert not user.has_perm('read')
