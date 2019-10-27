from django.contrib import admin
from django.db.models.functions import Lower

from MangAdventure.utils import filters
from MangAdventure.utils.images import img_tag
from .models import Group, Member, Role


class MemberRoleInline(admin.StackedInline):
    model = Role
    extra = 1


class MemberAdmin(admin.ModelAdmin):
    inlines = (MemberRoleInline,)
    list_display = ('name', 'twitter', 'discord', 'irc', 'reddit')
    search_fields = ('name', 'twitter', 'discord', 'irc', 'reddit')
    list_filter = (
        ('roles__group__name', filters.related_filter('group')),
        ('roles__role', filters.related_filter('role')),
    )

    def get_ordering(self, request):
        return (Lower('name'),)


class GroupAdmin(admin.ModelAdmin):
    exclude = ('id',)
    list_display = ('logo_image', 'name', 'website', 'description')
    search_fields = ('name', 'website', 'description')
    list_display_links = ('name',)

    def get_ordering(self, request):
        return (Lower('name'),)

    def logo_image(self, obj):
        return img_tag(obj.logo, 'logo', height=25)

    logo_image.short_description = 'logo'


admin.site.register(Group, GroupAdmin)
admin.site.register(Member, MemberAdmin)
