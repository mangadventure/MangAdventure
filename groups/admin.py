"""Admin models for the groups app."""

from typing import Optional

from django.contrib import admin
from django.db.models.functions import Lower
# XXX: cannot be resolved under TYPE_CHECKING
from django.forms.models import BaseInlineFormSet, ModelForm
from django.forms.widgets import HiddenInput
# XXX: cannot be resolved under TYPE_CHECKING
from django.http import HttpRequest
from django.utils.html import format_html

from MangAdventure import filters, utils

from .models import Group, Member, Role


class MemberRoleInline(admin.StackedInline):
    """Inline admin model for :class:`~groups.models.Role`."""
    model = Role
    extra = 1

    def get_formset(self, request: 'HttpRequest',
                    obj: Optional[Role], **kwargs
                    ) -> 'BaseInlineFormSet':  # pragma: no cover
        formset = super().get_formset(request, obj, **kwargs)
        if 'group' in formset.form.base_fields:
            formset.form.base_fields['group'].queryset = \
                Group.objects.filter(manager_id=request.user.id)
        return formset


class MemberAdmin(admin.ModelAdmin):
    """Admin model for :class:`~groups.models.Member`."""
    inlines = (MemberRoleInline,)
    ordering = (Lower('name'),)
    list_display = ('name', '_twitter', 'discord', 'irc', '_reddit')
    search_fields = ('name', 'twitter', 'discord', 'irc', 'reddit')
    list_filter = (
        ('roles__group__name', filters.related_filter('group')),
        ('roles__role', filters.related_filter('role')),
    )

    def _twitter(self, obj: Member) -> str:
        if not obj.twitter:
            return ''
        return format_html(
            '<a href="https://twitter.com/{0}" rel="noopener noreferrer"'
            ' target="_blank">@{0}</a>', obj.twitter
        )

    _twitter.short_description = 'twitter'
    _twitter.admin_order_field = 'twitter'

    def _reddit(self, obj: Member) -> str:
        if not obj.reddit:
            return ''
        return format_html(
            '<a href="https://reddit.com/u/{0}" rel="noopener noreferrer"'
            ' target="_blank">/u/{0}</a>', obj.reddit
        )

    _reddit.short_description = 'reddit'
    _reddit.admin_order_field = 'reddit'


class GroupAdmin(admin.ModelAdmin):
    """Admin model for :class:`~groups.models.Group`."""
    exclude = ('id',)
    ordering = (Lower('name'),)
    list_display = ('image', 'name', '_website', 'manager', 'description')
    search_fields = ('name', 'website', 'description')
    list_display_links = ('name',)
    list_filter = (
        ('manager', filters.related_filter('manager')),
    )
    empty_value_display = 'N/A'

    def get_form(self, request: 'HttpRequest', obj: Optional[Group]
                 = None, change: bool = False, **kwargs) -> 'ModelForm':
        form = super().get_form(request, obj, change, **kwargs)
        if 'manager' in form.base_fields:
            form.base_fields['manager'].initial = request.user.id
            if not request.user.is_superuser:  # pragma: no cover
                form.base_fields['manager'].widget = HiddenInput()
        return form

    def image(self, obj: Group) -> str:
        """
        Get the logo of the group as an HTML ``<img>``.

        :param obj: A ``Group`` model instance.

        :return: An ``<img>`` tag with the group's logo.
        """
        return utils.img_tag(obj.logo, 'logo', height=25)

    image.short_description = 'logo'

    def _website(self, obj: Group) -> str:
        if not obj.website:
            return ''
        return format_html(
            '<a href="{0}" rel="noopener noreferrer"'
            ' target="_blank">{0}</a>', obj.website
        )

    _website.short_description = 'website'
    _website.admin_order_field = 'website'

    def has_change_permission(self, request: 'HttpRequest', obj:
                              Optional[Group] = None) -> bool:
        """
        Return ``True`` if editing the object is permitted.

        | Superusers can edit any group.
        | Scanlators can only edit groups they manage.

        :param request: The original request.
        :param obj: A ``Group`` model instance.

        :return: ``True`` if the user is allowed to edit the group.
        """
        if request.user.is_superuser or obj is None:
            return True
        return obj.manager_id == request.user.id

    def has_delete_permission(self, request: 'HttpRequest', obj:
                              Optional[Group] = None) -> bool:
        """
        Return ``True`` if deleting the object is permitted.

        | Superusers can delete any group.
        | Scanlators can only delete groups they manage.

        :param request: The original request.
        :param obj: A ``Group`` model instance.

        :return: ``True`` if the user is allowed to delete the group.
        """
        if request.user.is_superuser or obj is None:
            return True
        return obj.manager_id == request.user.id


admin.site.register(Group, GroupAdmin)
admin.site.register(Member, MemberAdmin)

__all__ = ['MemberRoleInline', 'MemberAdmin', 'GroupAdmin']
