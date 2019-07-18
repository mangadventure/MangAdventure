from django.contrib import admin
from django.forms import CheckboxSelectMultiple, ModelForm

from MangAdventure.utils import filters
from MangAdventure.utils.images import img_tag

from .models import (
    Artist, ArtistAlias, Author, AuthorAlias,
    Category, Chapter, Series, SeriesAlias
)


class SeriesAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SeriesAdminForm, self).__init__(*args, **kwargs)
        self.fields['categories'].widget.widget = CheckboxSelectMultiple()

    class Meta:
        model = Series
        fields = '__all__'


class SeriesAliasInline(admin.StackedInline):
    model = SeriesAlias
    extra = 1


class AuthorAliasInline(admin.StackedInline):
    model = AuthorAlias
    extra = 1


class ArtistAliasInline(admin.StackedInline):
    model = ArtistAlias
    extra = 1


class ChapterAdmin(admin.ModelAdmin):
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

    def preview(self, obj):
        return img_tag(obj.pages.first().image, 'preview', height=50)


class SeriesAdmin(admin.ModelAdmin):
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

    def cover_image(self, obj):
        return img_tag(obj.cover, 'cover', height=75)

    cover_image.short_description = 'cover'


class AuthorAdmin(admin.ModelAdmin):
    inlines = (AuthorAliasInline,)
    list_display = ('name',)
    search_fields = ('name', 'aliases__alias')


class ArtistAdmin(admin.ModelAdmin):
    inlines = (ArtistAliasInline,)
    list_display = ('name',)
    search_fields = ('name', 'aliases__alias')


class CategoryAdmin(admin.ModelAdmin):
    exclude = ('id',)
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

    def get_readonly_fields(self, request, obj=None):
        return ('name',) if obj else []


admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Category, CategoryAdmin)
