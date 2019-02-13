from . import views

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

app_name = 'users'

urlpatterns = [
]

