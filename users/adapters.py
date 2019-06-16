from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return request.GET.get('next', '/user')

    def get_logout_redirect_url(self, request):
        return request.POST.get('next', '/')


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, social_account):
        return request.POST.get('next', '/user')
