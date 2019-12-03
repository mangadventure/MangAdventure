from . import views

from django.urls import path as url

app_name = 'groups'

urlpatterns = [
    url('', views.all_groups, name='all_groups'),
    url('<int:g_id>/', views.group, name='group'),
]
