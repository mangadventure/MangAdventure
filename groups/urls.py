from . import views

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

app_name = 'groups'

urlpatterns = [
    url(r'^$', views.all_groups, name='all_groups'),
    url(r'^(?P<g_id>[0-9]+)/$', views.group, name='group'),
]
