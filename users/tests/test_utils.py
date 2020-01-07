from django.contrib.auth.models import User

from users import get_user_display

from . import UsersTestBase


class TestInitPy(UsersTestBase):
    def test_get_user_display_name(self):
        assert get_user_display(self.user) == 'evangelos ch'

    def test_get_user_display_username(self):
        user = User.objects.get(pk=2)
        assert get_user_display(user) == 'obs'
