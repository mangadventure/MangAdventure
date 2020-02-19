"""The URLconf of the users app."""

from django.urls import path

from allauth.urls import urlpatterns as allauth_urls

from .feeds import BookmarksAtom, BookmarksRSS
from .views import Bookmarks, EditUser, Logout, profile

#: The URL patterns of the users app.
urlpatterns = [
    path('', profile, name='user_profile'),
    path('edit/', EditUser.as_view(), name='user_edit'),
    path('logout/', Logout.as_view(), name='account_logout'),
    path('bookmarks/', Bookmarks.as_view(), name='user_bookmarks'),
    path('bookmarks.atom', BookmarksAtom(), name='user_bookmarks.atom'),
    path('bookmarks.rss', BookmarksRSS(), name='user_bookmarks.rss'),
    # path('comments/', include('commentary.urls')),
] + allauth_urls

__all__ = ['urlpatterns']
