from django.contrib.auth.models import User, Group
from django.contrib import admin
from constance import config
from .models import *

admin.site.site_header = '{} {}'.format(
    config.NAME, 'Administration')


class SeriesAliasInline(admin.StackedInline):
    model = SeriesAlias
    extra = 1


class AuthorAliasInline(admin.StackedInline):
    model = AuthorAlias
    extra = 1


class ArtistAliasInline(admin.StackedInline):
    model = ArtistAlias
    extra = 1


class SeriesAdmin(admin.ModelAdmin):
    inlines = [SeriesAliasInline]

    def get_readonly_fields(self, request, obj=None):
        return ['slug'] if obj else []


class AuthorAdmin(admin.ModelAdmin):
    inlines = [AuthorAliasInline]


class ArtistAdmin(admin.ModelAdmin):
    inlines = [ArtistAliasInline]


class ChapterAdmin(admin.ModelAdmin):
    exclude = ['url']


admin.site.register(Series, SeriesAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Chapter, ChapterAdmin)


admin.site.unregister(Group)
admin.site.unregister(User)

