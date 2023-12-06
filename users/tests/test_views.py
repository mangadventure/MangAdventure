from json import loads
from urllib.parse import urlencode

from django.urls import reverse

from pytest import mark

from users.models import Bookmark, User, UserProfile

from . import UsersTestBase


class UsersViewTestBase(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.client.force_login(self.user)
        UserProfile.objects.get_or_create(user_id=self.user.id)


class TestEditUser(UsersViewTestBase):
    URL = reverse('user_edit')
    CONTENT_TYPE = 'application/x-www-form-urlencoded'

    def setup_method(self):
        super().setup_method()
        self.data = {
            'user_id': 1,
            'email': 'test2@email.com',
            'curr_password': 'testerino',
            'new_password1': 'testpass2',
            'new_password2': 'testpass2',
            'username': 'rain2',
            'first_name': 'new',
            'last_name': 'name',
            'bio': 'test'
        }

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200

    def test_get_no_login(self):
        self.client.logout()
        r = self.client.get(self.URL)
        assert r.status_code == 302

    def test_post_no_login(self):
        self.client.logout()
        r = self.client.post(
            self.URL, content_type=self.CONTENT_TYPE, data=urlencode(self.data)
        )
        assert r.status_code == 302

    def test_post(self):
        r = self.client.post(
            self.URL, content_type=self.CONTENT_TYPE, data=urlencode(self.data)
        )
        assert r.status_code == 200

    def test_post_invalid(self):
        self.data['new_password1'] = 'test2'
        r = self.client.post(
            self.URL, content_type=self.CONTENT_TYPE, data=urlencode(self.data)
        )
        assert r.status_code == 200
        assert 'Error: please check the fields' in str(r.content)


class TestProfile(UsersViewTestBase):
    URL = reverse('user_profile')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200

    def test_get_specific(self):
        r = self.client.get(self.URL, data={'id': 2})
        assert r.status_code == 200

    def test_get_other_superuser(self):
        r = self.client.get(self.URL, data={'id': 3})
        assert r.status_code == 404

    def test_get_no_login(self):
        self.client.logout()
        r = self.client.get(self.URL)
        assert r.status_code == 302

    # https://github.com/pytest-dev/pytest-django/issues/754
    @mark.xfail(raises=User.DoesNotExist, reason='fails only in tests')
    def test_invalid_user(self):
        r = self.client.get(self.URL, data={'id': 5})
        assert r.status_code == 404

    def test_invalid_id(self):
        from math import nan
        r = self.client.get(self.URL, data={'id': nan})
        assert r.status_code == 404


class TestExport(UsersViewTestBase):
    URL = reverse('user_data')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200
        data = loads(r.getvalue().decode())
        assert data['username'] == self.user.username


class TestDelete(UsersViewTestBase):
    URL = reverse('user_delete')

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200

    def test_post(self):
        r = self.client.post(self.URL)
        assert r.status_code == 302


class TestBookmarks(UsersViewTestBase):
    URL = reverse('user_bookmarks')
    CONTENT_TYPE = 'application/x-www-form-urlencoded'

    def test_get(self):
        r = self.client.get(self.URL)
        assert r.status_code == 200

    def test_get_no_login(self):
        self.client.logout()
        r = self.client.get(self.URL)
        assert r.status_code == 302

    def test_post(self):
        r = self.client.post(
            self.URL, data=urlencode({'series': 1}),
            content_type=self.CONTENT_TYPE
        )
        assert r.status_code == 201

    def test_post_create(self):
        Bookmark.objects.create(user_id=self.user.id, series_id=2)
        r = self.client.post(
            self.URL, data=urlencode({'series': 2}),
            content_type=self.CONTENT_TYPE
        )
        assert r.status_code == 204
