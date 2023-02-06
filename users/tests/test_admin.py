from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest

from users.admin import (
    OAuthApp, OAuthAppAdmin, User, UserAdmin, UserForm, UserTypeFilter
)

from . import UsersTestBase


class TestUserTypeFilter(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.model = User
        self.model_admin = UserAdmin
        self.request = HttpRequest()
        self.request.user = self.user
        self.filter = UserTypeFilter(
            model=self.model, model_admin=self.model_admin,
            request=self.request, params={'type': 'superuser'}
        )

    def test_lookups(self):
        lookups = self.filter.lookups(self.request, self.model_admin)
        assert lookups == [
            ('superuser', 'Superuser'),
            ('staff', 'Staff'),
            ('scanlator', 'Scanlator'),
            ('regular', 'Regular')
        ]

    def test_queryset(self):
        queryset = self.filter.queryset(
            request=self.request, queryset=User.objects.all()
        )
        assert queryset.count() == 2


class TestUserAdmin(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.site = AdminSite()
        self.admin = UserAdmin(admin_site=self.site, model=User)

    def test_email(self):
        email_link = self.admin._email(self.user)
        assert email_link.startswith(f'<a href="mailto:{self.user.email}')

    def test_email_empty(self):
        email_link = self.admin._email(User.objects.get(pk=2))
        assert email_link == ''

    def test_full_name(self):
        assert self.admin.full_name(self.user) == 'evangelos ch'

    def test_has_add_permission(self):
        request = HttpRequest()
        assert not self.admin.has_add_permission(request)


class TestOAuthApp(UsersTestBase):
    def test_str(self):
        app = OAuthApp.objects.create(
            provider='reddit', name='whatever', client_id='whatever'
        )
        assert str(app) == 'whatever (reddit)'


class TestUserForm(UsersTestBase):
    def test_is_scanlator(self):
        form = UserForm()
        assert not form.fields['is_scanlator'].initial
        form = UserForm(instance=User.objects.get(pk=2))
        assert form.fields['is_scanlator'].initial


class TestOAuthAppAdmin(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.site = AdminSite()
        self.admin = OAuthAppAdmin(admin_site=self.site, model=OAuthApp)

    def test_provider(self):
        app = OAuthApp.objects.create(
            provider='reddit', name='whatever', client_id='whatever'
        )
        provider_url = self.admin._provider(app)
        assert '#reddit"' in provider_url
        assert 'reddit</a>' in provider_url

    def test_provider_empty(self):
        app = OAuthApp.objects.create(name='whatever', client_id='whatever')
        assert self.admin._provider(app) == ''
