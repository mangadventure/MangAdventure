from urllib.parse import urlencode

from django.urls import reverse

from . import UsersTestBase


class UsersViewTestBase(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.client.force_login(self.user)


class TestEditUser(UsersViewTestBase):
    URL = reverse("user_edit")
    CONTENT_TYPE = "application/x-www-form-urlencoded"

    def setup_method(self):
        super().setup_method()
        self.data = {
            "user_id": 1,
            "email": "test@email.com",
            "curr_password": "test",
            "new_password1": "test2",
            "new_password2": "test2",
            "username": "rain2",
            "first_name": "new",
            "last_name": "name",
            "bio": "test",
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
        r = self.client.post(self.URL, content_type=self.CONTENT_TYPE,
                             data=urlencode(self.data))
        assert r.status_code == 302

    def test_post(self):
        r = self.client.post(self.URL, content_type=self.CONTENT_TYPE,
                             data=urlencode(self.data))
        assert r.status_code == 200
