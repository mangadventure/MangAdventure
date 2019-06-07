from django.contrib.messages import get_messages, add_message
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib import admin, sites, redirects
from django.forms import ModelForm
from constance.admin import Config, ConstanceAdmin
from tinymce.widgets import TinyMCE


class InfoPageForm(FlatpageForm):
    class Meta:
        fields = '__all__'
        model = FlatPage
        widgets = {
            'content': TinyMCE(mce_attrs={
                'selector': '.django-tinymce',
                'theme': 'modern',
                'relative_urls': True,
                'plugins': 'textcolor colorpicker lists advlist '
                           'link charmap visualchars code table image',
                'menubar': 'edit view format table',
                'toolbar': ' | '.join([
                    'undo redo', 'cut copy paste',
                    'formatselect forecolor backcolor',
                    'alignleft aligncenter alignright alignjustify',
                    'bold italic underline strikethrough',
                    'bullist numlist', 'link unlink', 'charmap image'
                ]),
                'valid_children': '+body[style]',
                'extended_valid_elements': 'style[type]',
            })
        }


class InfoPageAdmin(FlatPageAdmin):
    change_list_template = 'admin/change_list.html'
    change_list_form = ModelForm
    form = InfoPageForm
    list_filter = []

    def get_readonly_fields(self, request, obj=None):
        return ['url']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class InfoPage(FlatPage):
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'constance'
        verbose_name = 'info page'


class Site(sites.models.Site):
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'constance'


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
        app_label = 'constance'


class RedirectAdmin(redirects.admin.RedirectAdmin):
    change_list_template = 'admin/change_list.html'
    change_list_form = ModelForm


class Settings(Config):
    class Meta(Config.Meta):
        verbose_name = 'settings'
        verbose_name_plural = 'settings'
    _meta = Meta()


admin.site.unregister([
    FlatPage, Config,
    sites.models.Site,
    redirects.models.Redirect
])
admin.site.register(Site, SiteAdmin)
admin.site.register(Redirect, RedirectAdmin)
admin.site.register(InfoPage, InfoPageAdmin)
admin.site.register([Settings], ConstanceAdmin)

