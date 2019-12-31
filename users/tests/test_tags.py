from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp

from users.templatetags.user_tags import available

from . import UsersTestBase


class TestAvailableSocialApps(UsersTestBase):
    def test_empty(self):
        all_providers = providers.registry.get_list()
        available_providers = available(all_providers)
        assert not available_providers

    def test_valid(self):
        SocialApp.objects.create(provider="discord",
                                 name="test", client_id="test")
        all_providers = providers.registry.get_list()
        available_providers = available(all_providers)
        assert len(available_providers) == 1
