from django.contrib.auth.models import User
from django.db import IntegrityError

from pytest import raises

from reader.models import Series
from users.models import ApiKey, Bookmark, UserProfile, _avatar_uploader

from . import UsersTestBase


class TestBookmark(UsersTestBase):
    def test_create(self):
        """Test object creation & relations."""
        bookmark = Bookmark.objects.create(user=self.user, series=self.series)
        assert bookmark.series == self.series
        assert bookmark.user == self.user
        assert self.user.bookmarks.count() == 1
        assert self.user.bookmarks.get(series=self.series)

    def test_integrity(self):
        """
        Test that series and user are unique together, but not individually.
        """
        Bookmark.objects.create(user=self.user, series=self.series)
        user2 = User.objects.get(pk=2)
        series2 = Series.objects.get(pk=2)
        assert Bookmark.objects.create(user=user2, series=self.series)
        assert Bookmark.objects.create(user=self.user, series=series2)

        with raises(IntegrityError):
            Bookmark.objects.create(user=self.user, series=self.series)


class TestUserProfile(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.profile = UserProfile.objects.create(user=self.user, bio='Test')

    def test_create(self):
        """Test object creation & relations."""
        assert self.profile.bio == 'Test'
        assert self.profile.user == self.user
        assert self.user.profile == self.profile
        assert str(self.profile) == str(self.user)
        assert hash(self.profile) > 0
        assert self.profile.get_absolute_url() \
            .endswith(f'?id={self.profile.id}')


class TestApiKey(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.key = ApiKey.objects.create(user=self.user, key='A' * 64)

    def test_create(self):
        """Test object creation."""
        assert self.key.key == 'A' * 64
        assert str(self.key) == 'A' * 64
        assert hash(self.key) > 0


class TestUtils(UsersTestBase):
    def test_avatar_uploader(self):
        profile = UserProfile.objects.create(user=self.user)
        upload_dir = _avatar_uploader(profile, 'whatever.png')
        assert upload_dir == f'users/{profile.pk}/avatar.png'
