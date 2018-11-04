from . import views

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

app_name = 'users'

urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^activate/$', views.activate, name='activate'),
    url(r'^logout$', views.user_logout, name='logout'),
    url(r'^reset/$', views.pass_reset, name='reset'),
]

