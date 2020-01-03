from django.http import HttpRequest

from allauth.socialaccount.models import SocialAccount

from users.adapters import AccountAdapter, SocialAccountAdapter

from . import UsersTestBase


class UserAdapterTestBase(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.request = HttpRequest()
        self.next_url = '/some/url'
        self.request.GET = {'next': self.next_url}
        self.request.POST = {'next': self.next_url}
        self.empty_request = HttpRequest()
        self.adapter = AccountAdapter()
        self.social_adapter = SocialAccountAdapter()


class TestAccountAdapter(UserAdapterTestBase):
    def test_get_login_redirect_url(self):
        assert self.next_url == self.adapter \
            .get_login_redirect_url(self.request)

    def test_get_login_redirect_url_no_next(self):
        assert '/user' == self.adapter \
            .get_login_redirect_url(self.empty_request)

    def test_get_logout_redirect_url(self):
        assert self.next_url == self.adapter \
            .get_logout_redirect_url(self.request)

    def test_get_logout_redirect_url_no_next(self):
        assert '/' == self.adapter \
            .get_logout_redirect_url(self.empty_request)


class TestSocialAccountAdapter(UserAdapterTestBase):
    def setup_method(self):
        super().setup_method()
        self.social_account = SocialAccount.objects.create(
            user=self.user, provider='reddit', uid='whatever'
        )

    def test_get_connect_redirect_url(self):
        assert self.next_url == self.social_adapter \
            .get_connect_redirect_url(self.request, self.social_account)

    def test_get_connect_redirect_url_no_next(self):
        assert '/user' == self.social_adapter \
            .get_connect_redirect_url(self.empty_request, self.social_account)
