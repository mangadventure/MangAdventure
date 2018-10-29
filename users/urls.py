from . import views

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

app_name = 'users'

urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.userlogin, name='login'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
        name='activate'),
    url(r'^logout$', views.userlogout, name='logout'),
    url(r'^reset/$', views.reset_prompt, name='reset_prompt'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.reset,
        name='reset')
]

