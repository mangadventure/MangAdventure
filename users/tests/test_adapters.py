from django.http import HttpRequest

from allauth.socialaccount.models import SocialAccount

from users.adapters import AccountAdapter, SocialAccountAdapter

from . import UsersTestBase


class UserAdapterTestBase(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.request = HttpRequest()
        self.next_url = "/some/url"
        self.request.GET = {
            "next": self.next_url
        }
        self.request.POST = {
            "next": self.next_url
        }
        self.empty_request = HttpRequest()


class TestAccountAdapter(UserAdapterTestBase):
    def test_get_login_redirect_url(self):
        assert AccountAdapter()\
            .get_login_redirect_url(self.request) == self.next_url

    def test_get_login_redirect_url_no_next(self):
        assert AccountAdapter()\
            .get_login_redirect_url(self.empty_request) == "/user"

    def test_get_logout_redirect_url(self):
        assert AccountAdapter()\
            .get_logout_redirect_url(self.request) == self.next_url

    def test_get_logout_redirect_url_no_next(self):
        assert AccountAdapter()\
            .get_logout_redirect_url(self.empty_request) == "/"


class TestSocialAccountAdapter(UserAdapterTestBase):
    def setup_method(self):
        super().setup_method()
        self.social_account = SocialAccount.objects.create(user=self.user,
                                                           provider="reddit",
                                                           uid="whatever")

    def test_get_connect_redirect_url(self):
        redirect_url = SocialAccountAdapter()\
            .get_connect_redirect_url(self.request, self.social_account)
        assert redirect_url == self.next_url

    def test_get_connect_redirect_url_no_next(self):
        redirect_url = SocialAccountAdapter() \
            .get_connect_redirect_url(self.empty_request, self.social_account)
        assert redirect_url == "/user"
