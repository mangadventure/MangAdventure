"""Admin models for the groups app."""

from django.contrib import admin
from django.db.models.functions import Lower

from MangAdventure.utils import filters
from MangAdventure.utils.images import img_tag

from .models import Group, Member, Role


class MemberRoleInline(admin.StackedInline):
    """Inline admin model for :class:`~groups.models.Role`."""
    model = Role
    extra = 1


class MemberAdmin(admin.ModelAdmin):
    """Admin model for :class:`~groups.models.Member`."""
    inlines = (MemberRoleInline,)
    ordering = (Lower('name'),)
    list_display = ('name', 'twitter', 'discord', 'irc', 'reddit')
    search_fields = ('name', 'twitter', 'discord', 'irc', 'reddit')
    list_filter = (
        ('roles__group__name', filters.related_filter('group')),
        ('roles__role', filters.related_filter('role')),
    )


class GroupAdmin(admin.ModelAdmin):
    """Admin model for :class:`~groups.models.Group`."""
    exclude = ('id',)
    ordering = (Lower('name'),)
    list_display = ('logo_image', 'name', 'website', 'description')
    search_fields = ('name', 'website', 'description')
    list_display_links = ('name',)

    def logo_image(self, obj: Group) -> str:
        """
        Get the logo of the group as an HTML ``<img>``.

        :param obj: A ``Group`` model instance.

        :return: An ``<img>`` tag with the group's logo.
        """
        return img_tag(obj.logo, 'logo', height=25)

    logo_image.short_description = 'logo'


admin.site.register(Group, GroupAdmin)
admin.site.register(Member, MemberAdmin)

__all__ = ['MemberRoleInline', 'MemberAdmin', 'GroupAdmin']
