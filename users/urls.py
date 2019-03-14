from allauth.urls import urlpatterns as allauth_urls
from .views import profile, edit_user, PostOnlyLogoutView, bookmark

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

urlpatterns = [
    url(r'^$', profile, name='user_profile'),
    url(r'^edit/', edit_user, name='user_edit'),
    url(r'^logout/$', PostOnlyLogoutView.as_view(), name='account_logout'),
    url(r'^bookmark/$', bookmark, name='bookmark')
] + allauth_urls

