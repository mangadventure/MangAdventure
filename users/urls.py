"""The URLconf of the users app."""

from django.urls import path, re_path

from allauth.urls import urlpatterns as allauth_urls

from .feeds import BookmarksAtom, BookmarksRSS
from .views import Bookmarks, EditUser, Logout, PasswordReset, profile

#: The URL patterns of the users app.
urlpatterns = [
    path('', profile, name='user_profile'),
    path('edit/', EditUser.as_view(), name='user_edit'),
    path('logout/', Logout.as_view(), name='account_logout'),
    path('bookmarks/', Bookmarks.as_view(), name='user_bookmarks'),
    path('bookmarks.atom', BookmarksAtom(), name='user_bookmarks.atom'),
    path('bookmarks.rss', BookmarksRSS(), name='user_bookmarks.rss'),
    re_path(
        r'^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
        PasswordReset.as_view(),
        name='account_reset_password_from_key'
    )
] + allauth_urls

__all__ = ['urlpatterns']
