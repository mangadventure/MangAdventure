from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from django.http import HttpRequest

from config.admin import InfoPageAdmin, InfoPageForm, Site, SiteAdmin

from . import ConfigTestBase


def test_info_page_form_create():
    assert InfoPageForm()


class TestInfoPageAdmin:
    def setup_method(self):
        self.site = AdminSite()
        self.admin = InfoPageAdmin(admin_site=self.site, model=FlatPage)
        self.request = HttpRequest()

    def test_has_add_permission(self):
        assert not self.admin.has_add_permission(self.request)

    def test_has_delete_permission(self):
        assert not self.admin.has_delete_permission(self.request)


class TestSiteAdmin(ConfigTestBase):
    def setup_method(self):
        super().setup_method()
        self.site = AdminSite()
        self.admin = SiteAdmin(admin_site=self.site, model=Site)
        self.request = HttpRequest()
        self.request.user = self.user

    def test_has_delete_permission_superuser(self):
        assert self.admin.has_delete_permission(self.request)

    def test_has_delete_permission(self):
        self.request.user = User.objects.get(pk=2)
        assert not self.admin.has_delete_permission(self.request)

    def test_has_delete_permission_site(self):
        site = Site.objects.get(pk=1)
        assert not self.admin.has_delete_permission(self.request, site)
