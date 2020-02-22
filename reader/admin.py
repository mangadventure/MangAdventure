"""Admin models for the reader app."""

from typing import Optional, Tuple

from django.contrib import admin
from django.db.models.query import Q, QuerySet
from django.forms.models import BaseInlineFormSet, ModelForm
# XXX: Forward reference warning when under TYPE_CHECKING
from django.http import HttpRequest
from django.utils.html import mark_safe

from MangAdventure import filters, utils

from .models import (
    Artist, ArtistAlias, Author, AuthorAlias,
    Category, Chapter, Page, Series, SeriesAlias
)


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


class PageFormset(BaseInlineFormSet):
    """Formset for :class:`~reader.admin.PageInline`."""

    def clean(self):  # pragma: no cover
        """Ensure that page numbers don't have duplicates."""
        super().clean()
        numbers = []
        for form in self.forms:
            num = form.cleaned_data.get('number')
            if num in numbers:
                form._errors['number'] = \
                    self.error_class([self.get_form_error()])
                del form.cleaned_data['number']
            if not form.cleaned_data.get('DELETE'):
                numbers.append(num)


class PageInline(admin.TabularInline):
    """
    Inline admin model for :class:`~reader.models.Page`.

    .. admonition:: TODO
       :class: warning

       Add a way to delete all the pages.
    """
    model = Page
    extra = 1
    formset = PageFormset
    fields = ('image', 'preview', 'number')
    readonly_fields = ('preview',)

    def preview(self, obj: Page) -> str:
        """
        Get the image of the page as an HTML ``<img>``.

        :param obj: A ``Page`` model instance.

        :return: An ``<img>`` tag with the page image.
        """
        return utils.img_tag(obj.image, 'preview', height=150)

    preview.short_description = ''


class ChapterAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Chapter`."""
    inlines = (PageInline,)
    date_hierarchy = 'uploaded'
    list_display = (
        'preview', 'title', 'volume', '_number',
        'uploaded', 'modified', 'final'
    )
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
    actions = ('toggle_final',)
    empty_value_display = 'N/A'

    def _number(self, obj: Chapter) -> str:
        return f'{obj.number:g}'

    _number.short_description = 'number'
    _number.admin_order_field = 'number'

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

    def toggle_final(self, request: 'HttpRequest', queryset: 'QuerySet'):
        """
        Toggle the status of the selected chapters.

        :param request: The original request.
        :param queryset: The original queryset.
        """
        queryset.update(final=Q(final=False))

    toggle_final.short_description = 'Toggle status of selected chapters'


class SeriesForm(ModelForm):
    """Admin form for :class:`~reader.models.Series`."""
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super().__init__(*args, **kwargs)
        self.fields['format'].help_text = mark_safe('<br>'.join((
            'The format used to render the chapter names.'
            ' The following variables are available:',
            '<b>{title}</b>: The title of the chapter.',
            '<b>{volume}</b>: The volume of the chapter.',
            '<b>{number}</b>: The number of the chapter.',
            '<b>{date}</b>: The chapter\'s upload date (YYYY-MM-DD).',
            '<b>{series}</b>: The title of the series.'
        )))

    class Meta:
        model = Series
        fields = '__all__'


class SeriesAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Series`."""
    form = SeriesForm
    inlines = (SeriesAliasInline,)
    list_display = ('cover_image', 'title', 'created', 'modified', 'completed')
    list_display_links = ('title',)
    date_hierarchy = 'created'
    ordering = ('-modified',)
    search_fields = ('title',)
    autocomplete_fields = ('categories',)
    list_filter = (
        ('authors', filters.related_filter('author')),
        ('artists', filters.related_filter('artist')),
        ('categories', filters.related_filter('category')),
        filters.boolean_filter(
            'status', 'completed', ('Completed', 'Ongoing')
        )
    )
    actions = ('toggle_completed',)
    empty_value_display = 'N/A'

    def cover_image(self, obj: Series) -> str:
        """
        Get the cover of the series as an HTML ``<img>``.

        :param obj: A ``Series`` model instance.

        :return: An ``<img>`` tag with the series cover.
        """
        return utils.img_tag(obj.cover, 'cover', height=75)

    cover_image.short_description = 'cover'

    def toggle_completed(self, request: 'HttpRequest', queryset: 'QuerySet'):
        """
        Toggle the status of the selected series.

        :param request: The original request.
        :param queryset: The original queryset.
        """
        queryset.update(completed=Q(completed=False))

    toggle_completed.short_description = 'Toggle status of selected series'


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
    'SeriesAliasInline', 'AuthorAliasInline',
    'ArtistAliasInline', 'ChapterAdmin', 'SeriesAdmin',
    'AuthorAdmin', 'ArtistAdmin', 'CategoryAdmin'
]
