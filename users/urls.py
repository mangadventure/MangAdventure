from allauth.urls import urlpatterns as allauth_urls
from .views import profile

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

app_name = 'users'

urlpatterns = [url(r'^$', profile, name='profile')] + allauth_urls

