from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.contrib import admin
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import (
    SocialApp, SocialAccount, SocialToken
)
from .models import User


class UserAdmin(admin.ModelAdmin):
    exclude = ['password', 'groups']


class OAuthApp(SocialApp):
    class Meta:
        proxy = True
        app_label = User._meta.app_label
        verbose_name = 'OAuth App'
        verbose_name_plural = 'OAuth Apps'

    def __str__(self):
        return '%s (%s)' % (self.name, self.provider)


admin.site.unregister(Site)
admin.site.unregister(EmailAddress)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(OAuthApp)

