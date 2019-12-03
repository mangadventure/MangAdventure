from django.contrib import admin
from django.contrib.auth import models

from allauth.account.models import EmailAddress
from allauth.socialaccount.admin import SocialAppAdmin
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken

from MangAdventure.utils.filters import boolean_filter

# from commentary.admin import CommentsAdmin
# from commentary.models import Comment


class UserTypeFilter(admin.SimpleListFilter):
    title = 'type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return (
            ('superuser', 'Superuser'),
            ('staff', 'Staff'),
            ('regular', 'Regular')
        )

    def queryset(self, request, queryset):
        return {
            'superuser': queryset.filter(is_superuser=True),
            'staff': queryset.filter(is_staff=True),
            'regular': queryset.exclude(is_staff=True)
        }.get(self.value(), queryset)


class User(models.User):
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'users'
        verbose_name = 'user'


class UserAdmin(admin.ModelAdmin):
    exclude = ('password', 'groups')
    list_display = ('username', 'email', 'full_name', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (
        boolean_filter('status', 'is_active', ('Active', 'Inactive')),
        UserTypeFilter,
    )
    ordering = ('username',)

    def full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    def has_add_permission(self, request):
        return False


class OAuthApp(SocialApp):
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'users'
        verbose_name = 'OAuth app'

    def __str__(self):
        return '%s (%s)' % (self.name, self.provider)


class OAuthAppAdmin(SocialAppAdmin):
    list_display = ('name', 'provider', 'client_id')


# class UserComment(Comment):
#     class Meta:
#         proxy = True
#         auto_created = True
#         app_label = 'users'


# class UserCommentAdmin(CommentsAdmin):
#     def has_add_permission(self, request):
#         return False


admin.site.unregister([
    EmailAddress, SocialAccount, SocialToken,
    SocialApp, models.User, models.Group
])
admin.site.register(User, UserAdmin)
admin.site.register(OAuthApp, OAuthAppAdmin)
# admin.site.register(UserComment, UserCommentAdmin)
