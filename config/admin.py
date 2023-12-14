"""The admin models of the config app."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.models import FlatPage
from django.contrib.redirects.admin import RedirectAdmin as _RedirectAdmin
from django.contrib.redirects.models import Redirect as _Redirect
from django.contrib.sites.admin import SiteAdmin as _SiteAdmin
from django.contrib.sites.models import Site as _Site
from django.forms import ModelForm

from MangAdventure.widgets import TinyMCE

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest

admin.site.site_header = f'{settings.CONFIG["NAME"]} Administration'
admin.site.site_title = admin.site.site_header


class InfoPageForm(FlatpageForm):
    """Admin form for :class:`InfoPage`."""

    def __init__(self, *args, **kwargs):
        # HACK: bypass FlatpageForm.__init__
        super(FlatpageForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = '__all__'
        model = FlatPage
        widgets = {
            'content': TinyMCE(attrs={
                'mce_plugins': 'textcolor colorpicker lists advlist link'
                               ' charmap visualchars code table image',
                'mce_menubar': 'edit view format table',
                'mce_toolbar': ' | '.join((
                    'undo redo', 'cut copy paste',
                    'formatselect forecolor backcolor',
                    'alignleft aligncenter alignright alignjustify',
                    'bold italic underline strikethrough',
                    'bullist numlist', 'link unlink image charmap'
                )),
                'mce_valid_children': '+body[style]',
                'mce_extended_valid_elements': 'style[type]',
            })
        }


class InfoPage(FlatPage):
    """:class:`django.contrib.flatpages.admin.FlatPage` proxy model."""
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'config'
        verbose_name = 'info page'


class InfoPageAdmin(FlatPageAdmin):
    """Admin model for :class:`InfoPage`."""
    change_list_template = 'admin/change_list.html'
    change_list_form = ModelForm
    form = InfoPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
    )
    readonly_fields = ('url',)
    list_filter = ()

    def has_add_permission(self, request: HttpRequest) -> bool:
        """
        Return whether adding an ``InfoPage`` object is permitted.

        :param request: The original request.

        :return: Always returns ``False``.
        """
        return False

    def has_delete_permission(self, request: HttpRequest,
                              obj: InfoPage | None = None) -> bool:
        """
        Return whether deleting an ``InfoPage`` object is permitted.

        :param request: The original request.
        :param obj: The object to be deleted.

        :return: Always returns ``False``.
        """
        return False


class Site(_Site):
    """:class:`django.contrib.sites.models.Site` proxy model."""
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'config'


class SiteAdmin(_SiteAdmin):
    """Admin model for :class:`Site`."""
    change_list_template = 'admin/change_list.html'
    change_list_form = ModelForm

    def has_delete_permission(self, request: HttpRequest,
                              obj: Site | None = None) -> bool:
        """
        Return whether deleting a ``Site`` object is permitted.

        :param request: The original request.
        :param obj: The object to be deleted.

        :return: Returns ``False`` for the first site, otherwise calls
                 :meth:`django.contrib.admin.ModelAdmin.has_delete_permission`.
        """
        if getattr(obj, 'pk', 0) == 1:
            return False
        return super().has_delete_permission(request, obj)


class Redirect(_Redirect):
    """:class:`django.contrib.redirects.models.Redirect` proxy model."""
    class Meta:
        proxy = True
        auto_created = True
        app_label = 'config'


class RedirectAdmin(_RedirectAdmin):
    """Admin model for :class:`Redirect`."""
    change_list_template = 'admin/change_list.html'
    change_list_form = ModelForm


admin.site.unregister((FlatPage, _Site, _Redirect))
admin.site.register(Site, SiteAdmin)
admin.site.register(Redirect, RedirectAdmin)
admin.site.register(InfoPage, InfoPageAdmin)

__all__ = [
    'InfoPageForm', 'InfoPageAdmin', 'InfoPage',
    'Site', 'SiteAdmin', 'Redirect', 'RedirectAdmin'
]
