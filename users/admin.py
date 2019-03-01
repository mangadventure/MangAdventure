from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.contrib import admin
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import (
    SocialApp, SocialAccount, SocialToken
)


class UserAdmin(admin.ModelAdmin):
    exclude = ['password', 'groups']


class OAuthApp(SocialApp):
    class Meta:
        proxy = True
        auto_created = True
        app_label = User._meta.app_label
        verbose_name = 'OAuth App'
        verbose_name_plural = 'OAuth Apps'

    def __str__(self):
        return '%s (%s)' % (self.name, self.provider)


admin.site.unregister([
    Site, EmailAddress, SocialAccount,
    SocialToken, SocialApp, User, Group
])
admin.site.register(User, UserAdmin)
admin.site.register(OAuthApp)

