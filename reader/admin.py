"""Admin models for the reader app."""

from typing import Optional, Tuple

from django.contrib import admin
from django.forms import CheckboxSelectMultiple, ModelForm
# XXX: Forward reference warning when under TYPE_CHECKING
from django.http import HttpRequest

from MangAdventure import filters, utils

from .models import (
    Artist, ArtistAlias, Author, AuthorAlias,
    Category, Chapter, Series, SeriesAlias
)


class SeriesAdminForm(ModelForm):
    """Admin form for :class:`~reader.models.Series`."""
    def __init__(self, *args, **kwargs):
        super(SeriesAdminForm, self).__init__(*args, **kwargs)
        self.fields['categories'].widget.widget = CheckboxSelectMultiple()

    class Meta:
        model = Series
        fields = '__all__'


class SeriesAliasInline(admin.StackedInline):
    """Inline admin model for :class:`~reader.models.SeriesAlias`."""
    model = SeriesAlias
    extra = 1


class AuthorAliasInline(admin.StackedInline):
    """Inline admin model for :class:`~reader.models.AuthorAlias`."""
    model = AuthorAlias
    extra = 1


class ArtistAliasInline(admin.StackedInline):
    """Inline admin model for :class:`~reader.models.ArtistAlias`."""
    model = ArtistAlias
    extra = 1


class ChapterAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Chapter`."""
    date_hierarchy = 'uploaded'
    list_display = ('preview', 'title', 'uploaded', 'modified', 'final')
    list_display_links = ('title',)
    ordering = ('-modified',)
    search_fields = ('title', 'series__title')
    list_filter = (
        ('series', admin.RelatedFieldListFilter),
        ('groups', filters.related_filter('group')),
        filters.boolean_filter(
            'status', 'final', ('Final', 'Not final')
        )
    )
    empty_value_display = 'N/A'

    def preview(self, obj: Chapter) -> str:
        """
        Get the first image of the chapter as an HTML ``<img>``.

        :param obj: A ``Chapter`` model instance.

        :return: An ``<img>`` tag with the chapter preview.
        """
        page = obj.pages.only('image').first()
        if page is None:
            return ''
        return utils.img_tag(page.image, 'preview', height=50)


class SeriesAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Series`."""
    inlines = (SeriesAliasInline,)
    form = SeriesAdminForm
    list_display = ('cover_image', 'title', 'modified', 'completed')
    list_display_links = ('title',)
    date_hierarchy = 'modified'
    ordering = ('-modified',)
    search_fields = ('title',)
    list_filter = (
        ('authors', filters.related_filter('author')),
        ('artists', filters.related_filter('artist')),
        ('categories', filters.related_filter('category')),
        filters.boolean_filter(
            'status', 'completed', ('Completed', 'Ongoing')
        )
    )
    empty_value_display = 'N/A'

    def cover_image(self, obj: Series) -> str:
        """
        Get the cover of the series as an HTML ``<img>``.

        :param obj: A ``Series`` model instance.

        :return: An ``<img>`` tag with the series cover.
        """
        return utils.img_tag(obj.cover, 'cover', height=75)

    cover_image.short_description = 'cover'


class AuthorAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Author`."""
    inlines = (AuthorAliasInline,)
    list_display = ('name', 'aliases')
    search_fields = ('name', 'aliases__alias')

    def aliases(self, obj: Author) -> str:
        """
        Get the author's aliases as a string.

        :param obj: An ``Author`` model instance.

        :return: A comma-separated list of aliases.
        """
        return ', '.join(obj.aliases.values_list('alias', flat=True))


class ArtistAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Artist`."""
    inlines = (ArtistAliasInline,)
    list_display = ('name', 'aliases')
    search_fields = ('name', 'aliases__alias')

    def aliases(self, obj: Artist) -> str:
        """
        Get the artist's aliases as a string.

        :param obj: An ``Artist`` model instance.

        :return: A comma-separated list of aliases.
        """
        return ', '.join(obj.aliases.values_list('alias', flat=True))


class CategoryAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Category`."""
    exclude = ('id',)
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

    def get_readonly_fields(self, request: 'HttpRequest', obj:
                            Optional[Category] = None) -> Tuple:
        """
        Return the fields that cannot be changed.

        Once a ``Category`` object has been created, its
        :attr:`~reader.models.Category.name` cannot be altered.

        :param request: The original request.
        :param obj: A ``Category`` model instance.

        :return: A tuple of readonly fields.
        """
        return ('name',) if obj else ()


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Category, CategoryAdmin)

__all__ = [
    'SeriesAdminForm', 'SeriesAliasInline',
    'AuthorAliasInline', 'ArtistAliasInline',
    'ChapterAdmin', 'SeriesAdmin', 'AuthorAdmin',
    'ArtistAdmin', 'CategoryAdmin'
]
