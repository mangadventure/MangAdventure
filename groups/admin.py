"""Admin models for the groups app."""

from django.contrib import admin
from django.db.models.functions import Lower
from django.utils.html import format_html

from MangAdventure import filters, utils

from .models import Group, Member, Role


class MemberRoleInline(admin.StackedInline):
    """Inline admin model for :class:`~groups.models.Role`."""
    model = Role
    extra = 1


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
    list_display = ('image', 'name', '_website', 'description')
    search_fields = ('name', 'website', 'description')
    list_display_links = ('name',)

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


admin.site.register(Group, GroupAdmin)
admin.site.register(Member, MemberAdmin)

__all__ = ['MemberRoleInline', 'MemberAdmin', 'GroupAdmin']
