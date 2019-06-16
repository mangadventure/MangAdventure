from django.contrib import admin
from django.forms import CheckboxSelectMultiple, ModelForm

from constance import config

from .models import (
    Artist, ArtistAlias, Author, AuthorAlias,
    Category, Chapter, Series, SeriesAlias
)

admin.site.site_header = config.NAME + ' Administration'


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


class SeriesAdmin(admin.ModelAdmin):
    inlines = [SeriesAliasInline]
    form = SeriesAdminForm


class AuthorAdmin(admin.ModelAdmin):
    inlines = [AuthorAliasInline]


class ArtistAdmin(admin.ModelAdmin):
    inlines = [ArtistAliasInline]


class CategoryAdmin(admin.ModelAdmin):
    exclude = ['id']

    def get_readonly_fields(self, request, obj=None):
        return ['name'] if obj else []


admin.site.register(Chapter)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Category, CategoryAdmin)
