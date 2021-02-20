"""Admin models for the reader app."""

from hashlib import blake2b
from typing import Optional, Tuple, Type

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.db.models import Q, QuerySet
# XXX: cannot be resolved under TYPE_CHECKING
from django.forms.models import BaseInlineFormSet, ModelForm
from django.forms.widgets import HiddenInput
# XXX: cannot be resolved under TYPE_CHECKING
from django.http import HttpRequest
from django.utils import timezone as tz
from django.utils.html import mark_safe

from MangAdventure import filters, utils

from .models import Alias, Artist, Author, Category, Chapter, Page, Series


class DateFilter(admin.DateFieldListFilter):
    """Admin interface filter for dates."""
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super().__init__(*args, **kwargs)
        self.title = 'date'
        self.links += (('Scheduled', {
            self.lookup_kwarg_since: tz.now()
        }),)


class PageFormset(BaseInlineFormSet):  # pragma: no cover
    """Formset for :class:`~reader.admin.PageInline`."""

    def clean(self):
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

    def save_existing(self, form: ModelForm, instance: Page,
                      commit: bool = True) -> Page:
        """Replace an existing chapter page."""
        with form.instance.image.open('rb') as img:
            dgst = blake2b(img.read(), digest_size=16)
            ext = form.instance.image.name.split(".")[-1]
            path = form.instance.chapter.get_directory()
            name = str(path / f'{dgst.hexdigest()}.{ext}')
            form.instance.image.name = name
            return form.save(commit=commit)

    def save_new(self, form: ModelForm, commit: bool = True) -> Page:
        """Add a new page to the chapter."""
        setattr(form.instance, self.fk.name, self.instance)
        return self.save_existing(form, self.instance, commit)


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
    date_hierarchy = 'published'
    list_display = (
        'preview', 'title', 'volume', '_number',
        'published', 'modified', 'final'
    )
    list_display_links = ('title',)
    ordering = ('-modified',)
    search_fields = ('title', 'series__title')
    list_filter = (
        ('series', admin.RelatedFieldListFilter),
        ('groups', filters.related_filter('group')),
        filters.boolean_filter(
            'status', 'final', ('Final', 'Not final')
        ),
        ('published', DateFilter),
        ('series__manager', filters.related_filter('manager')),
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

    def get_form(self, request: 'HttpRequest',
                 obj: Optional[Chapter], **kwargs
                 ) -> ModelForm:  # pragma: no cover
        form = super().get_form(request, obj, **kwargs)
        if 'series' in form.base_fields:
            form.base_fields['series'].queryset = \
                Series.objects.filter(manager_id=request.user.id)
        return form

    def has_change_permission(self, request: 'HttpRequest', obj:
                              Optional[Chapter] = None) -> bool:
        """
        Return ``True`` if editing the object is permitted.

        | Superusers can edit any chapter.
        | Scanlators can only edit chapters of series they manage.

        :param request: The original request.
        :param obj: A ``Chapter`` model instance.

        :return: ``True`` if the user is allowed to edit the chapter.
        """
        if request.user.is_superuser or obj is None:
            return True
        return obj.series.manager_id == request.user.id

    def has_delete_permission(self, request: 'HttpRequest', obj:
                              Optional[Chapter] = None) -> bool:
        """
        Return ``True`` if deleting the object is permitted.

        | Superusers delete edit any chapter.
        | Scanlators can only delete chapters of series they manage.

        :param request: The original request.
        :param obj: A ``Chapter`` model instance.

        :return: ``True`` if the user is allowed to delete the chapter.
        """
        if request.user.is_superuser or obj is None:
            return True
        return obj.series.manager_id == request.user.id


# TODO: find a cleaner way to adapt the help_text
def alias_inline(model: str) -> Type[GenericStackedInline]:
    """
    Get an inline admin model for :class:`~reader.models.Alias`.

    :param model: The name of the model that holds the alias.
    """
    class _AliasForm(ModelForm):
        def __init__(self, *args, **kwargs):  # pragma: no cover
            super().__init__(*args, **kwargs)
            self.fields['name'].help_text = f'Another name for this {model}.'

        class Meta:
            model = Alias
            fields = '__all__'

    class _AliasInline(GenericStackedInline):  # pragma: no cover
        form = _AliasForm
        model = Alias
        extra = 1

    return _AliasInline


class SeriesAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Series`."""
    inlines = (alias_inline('series'),)
    list_display = (
        'cover_image', 'title', 'manager',
        'created', 'modified', 'completed'
    )
    list_display_links = ('title',)
    date_hierarchy = 'created'
    ordering = ('-modified',)
    search_fields = ('title', 'aliases__name')
    autocomplete_fields = ('categories',)
    list_filter = (
        ('authors', filters.related_filter('author')),
        ('artists', filters.related_filter('artist')),
        ('categories', filters.related_filter('category')),
        filters.boolean_filter(
            'status', 'completed', ('Completed', 'Ongoing')
        ),
        ('manager', filters.related_filter('manager')),
    )
    actions = ('toggle_completed',)
    empty_value_display = 'N/A'

    def get_form(self, request: 'HttpRequest', obj: Optional[Series]
                 = None, change: bool = False, **kwargs) -> ModelForm:
        form = super().get_form(request, obj, change, **kwargs)
        if 'format' in form.base_fields:
            form.base_fields['format'].help_text = mark_safe('<br>'.join((
                'The format used to render the chapter names.'
                ' The following variables are available:',
                '<b>{title}</b>: The title of the chapter.',
                '<b>{volume}</b>: The volume of the chapter.',
                '<b>{number}</b>: The number of the chapter.',
                '<b>{date}</b>: The chapter\'s upload date (YYYY-MM-DD).',
                '<b>{series}</b>: The title of the series.'
            )))
        if 'manager' in form.base_fields:
            form.base_fields['manager'].initial = request.user.id
            if not request.user.is_superuser:  # pragma: no cover
                form.base_fields['manager'].widget = HiddenInput()
        return form

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

    def has_change_permission(self, request: 'HttpRequest', obj:
                              Optional[Series] = None) -> bool:
        """
        Return ``True`` if editing the object is permitted.

        | Superusers can edit any series.
        | Scanlators can only edit series they manage.

        :param request: The original request.
        :param obj: A ``Series`` model instance.

        :return: ``True`` if the user is allowed to edit the series.
        """
        if request.user.is_superuser or obj is None:
            return True
        return obj.manager_id == request.user.id

    def has_delete_permission(self, request: 'HttpRequest', obj:
                              Optional[Series] = None) -> bool:
        """
        Return ``True`` if deleting the object is permitted.

        | Superusers can delete any series.
        | Scanlators can only delete series they manage.

        :param request: The original request.
        :param obj: A ``Series`` model instance.

        :return: ``True`` if the user is allowed to delete the series.
        """
        if request.user.is_superuser or obj is None:
            return True
        return obj.manager_id == request.user.id


class AuthorAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Author`."""
    inlines = (alias_inline('author'),)
    list_display = ('name', 'aliases')
    search_fields = ('name', 'aliases__name')

    def aliases(self, obj: Author) -> str:
        """
        Get the author's aliases as a string.

        :param obj: An ``Author`` model instance.

        :return: A comma-separated list of aliases.
        """
        return ', '.join(obj.aliases.names())


class ArtistAdmin(admin.ModelAdmin):
    """Admin model for :class:`~reader.models.Artist`."""
    inlines = (alias_inline('artist'),)
    exclude = ('aliases',)
    list_display = ('name', 'aliases')
    search_fields = ('name', 'aliases__name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def aliases(self, obj: Artist) -> str:
        """
        Get the artist's aliases as a string.

        :param obj: An ``Artist`` model instance.

        :return: A comma-separated list of aliases.
        """
        return ', '.join(obj.aliases.names())


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
    'alias_inline', 'ChapterAdmin', 'SeriesAdmin',
    'AuthorAdmin', 'ArtistAdmin', 'CategoryAdmin'
]
