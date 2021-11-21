from allauth.socialaccount.models import SocialApp

from users.templatetags.user_tags import get_oauth_providers

from . import UsersTestBase


class TestAvailableSocialApps(UsersTestBase):
    def test_empty(self):
        assert not get_oauth_providers()

    def test_valid(self):
        SocialApp.objects.create(
            provider='discord', name='test', client_id='test'
        )
        assert len(get_oauth_providers()) == 1
