from pytest import mark

from MangAdventure.tests import get_big_image, get_test_image

from users.forms import UserProfileForm
from users.models import UserProfile

from . import UsersTestBase


class TestUserProfileForm(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.data = {
            "email": "test@email.com",
            "curr_password": "test",
            "new_password1": "testpass2",
            "new_password2": "testpass2",
            "username": "rain2",
            "first_name": "new",
            "last_name": "name",
            "bio": "test",
        }
        self.files = {
            "avatar": get_test_image()
        }
        self.profile = UserProfile.objects.create(user=self.user)

    def test_valid(self):
        form = UserProfileForm(data=self.data, instance=self.profile)
        assert form.is_valid()

    @mark.parametrize("field", ["email", "curr_password", "username"])
    def test_required(self, field):
        del self.data[field]
        form = UserProfileForm(data=self.data, instance=self.profile)
        assert not form.is_valid()

    def test_short_username(self):
        self.data["username"] = ""
        form = UserProfileForm(data=self.data, instance=self.profile)
        assert not form.is_valid()

    def test_short_passwords(self):
        self.data["new_password1"] = "test2"
        self.data["new_password2"] = "test2"
        form = UserProfileForm(data=self.data, instance=self.profile)
        assert not form.is_valid()

    def test_save(self):
        form = UserProfileForm(data=self.data, files=self.files,
                               instance=self.profile)
        form.save()
        self.profile.refresh_from_db()
        assert self.profile.user.first_name == "new"
        assert self.profile.user.last_name == "name"
        assert self.profile.bio == "test"
        assert self.profile.user.username == "rain2"

    def test_mismatching_passwords(self):
        self.data["new_password1"] = "testpass2"
        self.data["new_password2"] = "testpass3"
        form = UserProfileForm(data=self.data, instance=self.profile)
        assert not form.is_valid()

    def test_wrong_password(self):
        self.data["curr_password"] = "test12345"
        form = UserProfileForm(data=self.data, instance=self.profile)
        assert not form.is_valid()

    def test_taken_username(self):
        self.data["username"] = "obs"
        form = UserProfileForm(data=self.data, instance=self.profile)
        assert not form.is_valid()

    def test_big_file(self):
        self.files['avatar'] = get_big_image(3)
        form = UserProfileForm(data=self.data, files=self.files,
                               instance=self.profile)
        assert not form.is_valid()
