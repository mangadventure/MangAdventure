from django.conf import settings
from django.contrib import admin, redirects, sites
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.models import FlatPage
from django.forms import ModelForm

from MangAdventure.widgets import TinyMCE

admin.site.site_header = settings.CONFIG['NAME'] + ' Administration'
admin.site.site_title = admin.site.site_header


class InfoPageForm(FlatpageForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = '__all__'
        model = FlatPage
        widgets = {
            'content': TinyMCE(attrs={
                'mce_plugins': 'textcolor colorpicker lists advlist link'
                               ' charmap visualchars code table image',
                'mce_menubar': 'edit view format table',
                'mce_toolbar': ' | '.join([
                    'undo redo', 'cut copy paste',
                    'formatselect forecolor backcolor',
                    'alignleft aligncenter alignright alignjustify',
                    'bold italic underline strikethrough',
                    'bullist numlist', 'link unlink image charmap'
                ]),
                'mce_valid_children': '+body[style]',
                'mce_extended_valid_elements': 'style[type]',
            })
        }


class InfoPageAdmin(FlatPageAdmin):
    change_list_template = 'admin/change_list.html'
    change_list_form = ModelForm
    form = InfoPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content')}),
    )
    readonly_fields = ('url',)
    list_filter = ()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class InfoPage(FlatPage):
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'config'
        verbose_name = 'info page'


class Site(sites.models.Site):
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'config'


class SiteAdmin(sites.admin.SiteAdmin):
    change_list_template = 'admin/change_list.html'
    change_list_form = ModelForm

    def has_delete_permission(self, request, obj=None):
        return getattr(obj, 'pk', 0) != 1 and \
            super(SiteAdmin, self).has_delete_permission(request, obj)


class Redirect(redirects.models.Redirect):
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'config'


class RedirectAdmin(redirects.admin.RedirectAdmin):
    change_list_template = 'admin/change_list.html'
    change_list_form = ModelForm


admin.site.unregister((
    FlatPage, sites.models.Site, redirects.models.Redirect
))
admin.site.register(Site, SiteAdmin)
admin.site.register(Redirect, RedirectAdmin)
admin.site.register(InfoPage, InfoPageAdmin)
