"""Admin models for the users app."""

from typing import List, Tuple, Type

from django.contrib import admin
from django.contrib.auth import models
from django.db.models.functions import Concat as C
from django.db.models.query import QuerySet, Value as V
from django.forms.models import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
# XXX: Forward reference warning when under TYPE_CHECKING
from django.http import HttpRequest
from django.utils.html import format_html

from allauth.account.models import EmailAddress
from allauth.socialaccount.admin import SocialAppAdmin
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken

from MangAdventure.filters import boolean_filter

# from commentary.admin import CommentsAdmin
# from commentary.models import Comment


class UserTypeFilter(admin.SimpleListFilter):
    """Admin interface filter for user types."""
    #: The title of the filter.
    title = 'type'
    #: The filter's query parameter.
    parameter_name = 'type'

    def lookups(self, request: 'HttpRequest', model_admin:
                Type[admin.ModelAdmin]) -> List[Tuple[str, str]]:
        """
        Return a list of lookups for this filter.

        The first element in each tuple is the value of the
        query parameter. The second element is the human-readable
        name for the option that will appear in the admin sidebar.


        :param request: The original request.
        :param model_admin: An admin model object.

        :return: The following list of tuples:

                 .. code-block:: python

                    [
                        ('superuser', 'Superuser'),
                        ('staff', 'Staff'),
                        ('regular', 'Regular')
                    ]
        """
        return [
            ('superuser', 'Superuser'),
            ('staff', 'Staff'),
            ('regular', 'Regular')
        ]

    def queryset(self, request: 'HttpRequest', queryset:
                 'QuerySet') -> 'QuerySet':
        """
        Return the filtered queryset based on
        the value provided in the query string.

        :param request: The original request.
        :param queryset: The original queryset.

        :return: A filtered queryset according to :meth:`lookups`.
        """
        return {
            'superuser': queryset.filter(is_superuser=True),
            'staff': queryset.filter(is_staff=True),
            'regular': queryset.exclude(is_staff=True)
        }.get(self.value(), queryset)


class User(models.User):
    """:class:`django.contrib.auth.models.User` proxy model."""
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'users'
        verbose_name = 'user'


class UserAdmin(admin.ModelAdmin):
    """Admin model for :class:`User`."""
    exclude = ('password', 'groups')
    list_display = (
        'username', '_email', 'full_name',
        'date_joined', 'is_active'
    )
    list_editable = ('is_active',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (
        boolean_filter('status', 'is_active', ('Active', 'Inactive')),
        UserTypeFilter,
    )
    ordering = ('username',)

    def _email(self, obj: User) -> str:
        if not obj.email:
            return ''
        return format_html(
            '<a href="mailto:{0}" rel="noopener noreferrer"'
            ' target="_blank">{0}</a>', obj.email
        )

    _email.short_description = 'e-mail address'
    _email.admin_order_field = 'email'

    def full_name(self, obj: User) -> str:
        """
        Get the full name of the user.

        :param obj: A ``User`` model instance.

        :return: The user's full name.
        """
        return obj.get_full_name()

    full_name.admin_order_field = C('first_name', V(' '), 'last_name')

    def has_add_permission(self, request: 'HttpRequest') -> bool:
        """
        Return whether adding an ``User`` object is permitted.

        :param request: The original request.

        :return: Always returns ``False``.
        """
        return False


class OAuthApp(SocialApp):
    """:class:`allauth.socialaccount.models.SocialApp` proxy model."""
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'users'
        verbose_name = 'OAuth app'

    def __str__(self) -> str:
        """
        Return a string representing the object.

        :return: The name and provider of the app.
        """
        return f'{self.name} ({self.provider})'


class OAuthAppForm(ModelForm):
    """Admin form for :class:`OAuthApp`."""
    def __init__(self, *args, **kwargs):
        super(OAuthAppForm, self).__init__(*args, **kwargs)
        self.fields['sites'].widget.widget = CheckboxSelectMultiple()

    class Meta:
        model = OAuthApp
        fields = '__all__'


class OAuthAppAdmin(SocialAppAdmin):
    """Admin model for :class:`OAuthApp`."""
    form = OAuthAppForm
    list_display = ('name', '_provider', 'client_id')
    radio_fields = {'provider': admin.HORIZONTAL}

    def _provider(self, obj: OAuthApp) -> str:
        if not obj.provider:
            return ''
        return format_html(
            '<a href="{}{}" rel="noopener noreferrer" target="_blank">{}</a>',
            'https://django-allauth.readthedocs.io/en/stable/providers.html#',
            obj.provider, obj.provider.capitalize()
        )

    _provider.short_description = 'provider'
    _provider.admin_order_field = 'provider'


# class UserComment(Comment):
#     class Meta:
#         proxy = True
#         auto_created = True
#         app_label = 'users'


# class UserCommentAdmin(CommentsAdmin):
#     def has_add_permission(self, request):
#         return False


admin.site.unregister((
    EmailAddress, SocialAccount, SocialToken,
    SocialApp, models.User, models.Group
))
admin.site.register(User, UserAdmin)
admin.site.register(OAuthApp, OAuthAppAdmin)
# admin.site.register(UserComment, UserCommentAdmin)

__all__ = [
    'UserTypeFilter', 'User', 'UserAdmin',
    'OAuthApp', 'OAuthAppForm', 'OAuthAppAdmin'
]
