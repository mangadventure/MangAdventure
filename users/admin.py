"""Admin models for the users app."""

from __future__ import annotations

from typing import List, Tuple, Type

from django.contrib import admin
from django.contrib.auth import models
from django.db.models.functions import Concat as C
from django.db.models.query import QuerySet, Value as V
from django.forms.fields import BooleanField
from django.forms.models import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
# XXX: cannot be resolved under TYPE_CHECKING
from django.http import HttpRequest
from django.utils.functional import cached_property
from django.utils.html import format_html

from allauth.account.models import EmailAddress
from allauth.socialaccount.admin import SocialAppAdmin
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken

from MangAdventure.filters import boolean_filter


class UserTypeFilter(admin.SimpleListFilter):
    """Admin interface filter for user types."""
    #: The title of the filter.
    title = 'type'
    #: The filter's query parameter.
    parameter_name = 'type'

    def lookups(self, request: HttpRequest, model_admin:
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
                        ('scanlator', 'Scanlator'),
                        ('regular', 'Regular')
                    ]
        """
        return [
            ('superuser', 'Superuser'),
            ('staff', 'Staff'),
            ('scanlator', 'Scanlator'),
            ('regular', 'Regular')
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
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
            'scanlator': queryset.filter(groups__name='Scanlator'),
            'regular': queryset.exclude(is_staff=True)
        }.get(self.value(), queryset)


class User(models.User):
    """:class:`django.contrib.auth.models.User` proxy model."""
    @cached_property
    def is_scanlator(self) -> bool:
        """Get the scanlator status of the user."""
        return self.groups.filter(name='Scanlator').exists()

    class Meta:
        proxy = True
        auto_created = True
        app_label = 'users'
        verbose_name = 'user'


class UserForm(ModelForm):
    """Admin form for :class:`User`."""
    #: Scanlator status.
    is_scanlator = BooleanField(
        label='Scanlator status',
        required=False, help_text=(
            'Designates whether the user has '
            '"groups" and "reader" permissions.'
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_scanlator'].initial = \
            'instance' in kwargs and self.instance.is_scanlator

    def save(self, commit: bool = True) -> User:   # pragma: no cover
        is_scanlator = self.cleaned_data.pop('is_scanlator', False)
        instance = super().save(commit=False)
        if is_scanlator and not instance.is_scanlator:
            instance.groups.add(
                models.Group.objects.get(name='Scanlator')
            )
            if commit:
                instance.save()
        elif not is_scanlator and instance.is_scanlator:
            instance.groups.remove(
                models.Group.objects.get(name='Scanlator')
            )
            if commit:
                instance.save()
        return instance

    class Meta:
        model = User
        fields = '__all__'


class UserAdmin(admin.ModelAdmin):
    """Admin model for :class:`User`."""
    form = UserForm
    exclude = ('password', 'groups')
    list_display = (
        'username', '_email', 'full_name', 'date_joined', 'is_active'
    )
    list_editable = ('is_active',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (
        boolean_filter('status', 'is_active', ('Active', 'Inactive')),
        UserTypeFilter,
    )
    ordering = ('username',)

    @admin.display(ordering='email', description='e-mail address')
    def _email(self, obj: User) -> str:
        if not obj.email:
            return ''
        return format_html(
            '<a href="mailto:{0}" rel="noopener noreferrer"'
            ' target="_blank">{0}</a>', obj.email
        )

    @admin.display(ordering=C('first_name', V(' '), 'last_name'))
    def full_name(self, obj: User) -> str:
        """
        Get the full name of the user.

        :param obj: A ``User`` model instance.

        :return: The user's full name.
        """
        return obj.get_full_name()

    def has_add_permission(self, request: HttpRequest) -> bool:
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


class OAuthAppAdmin(SocialAppAdmin):
    """Admin model for :class:`OAuthApp`."""
    list_display = ('name', '_provider', 'client_id')
    radio_fields = {'provider': admin.HORIZONTAL}

    def get_form(self, *args, **kwargs) -> ModelForm:  # pragma: no cover
        form = super().get_form(*args, **kwargs)
        form.base_fields['sites'].widget.widget = CheckboxSelectMultiple()
        return form

    @admin.display(ordering='provider', description='provider')
    def _provider(self, obj: OAuthApp) -> str:
        if not obj.provider:
            return ''
        return format_html(
            '<a href="{}{}" rel="noopener noreferrer" target="_blank">{}</a>',
            'https://django-allauth.readthedocs.io/en/stable/providers.html#',
            obj.provider, obj.provider.capitalize()
        )


admin.site.unregister((
    EmailAddress, SocialAccount, SocialToken,
    SocialApp, models.User, models.Group
))
admin.site.register(User, UserAdmin)
admin.site.register(OAuthApp, OAuthAppAdmin)

__all__ = [
    'UserTypeFilter', 'User', 'UserForm',
    'UserAdmin', 'OAuthApp', 'OAuthAppAdmin'
]
