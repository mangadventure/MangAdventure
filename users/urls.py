from allauth.urls import urlpatterns as allauth_urls

from .views import PostOnlyLogoutView, bookmarks, edit_user, profile

from django.urls import path as url

urlpatterns = [
    url('', profile, name='user_profile'),
    url('edit/', edit_user, name='user_edit'),
    url('logout/', PostOnlyLogoutView.as_view(), name='account_logout'),
    url('bookmarks/', bookmarks, name='user_bookmarks'),
    # url('comments/', include('commentary.urls')),
] + allauth_urls
