"""The URLconf of the users app."""

from django.urls import path

from allauth.urls import urlpatterns as allauth_urls

from .views import PostOnlyLogoutView, bookmarks, edit_user, profile

#: The URL patterns of the users app.
urlpatterns = [
    path('', profile, name='user_profile'),
    path('edit/', edit_user, name='user_edit'),
    path('logout/', PostOnlyLogoutView.as_view(), name='account_logout'),
    path('bookmarks/', bookmarks, name='user_bookmarks'),
    # path('comments/', include('commentary.urls')),
] + allauth_urls

__all__ = ['urlpatterns']
