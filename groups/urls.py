"""The URLconf of the groups app."""

from django.urls import path

from . import views

#: The URL namespace of the groups app.
app_name = 'groups'

#: The URL patterns of the groups app.
urlpatterns = [
    path('', views.all_groups, name='all_groups'),
    path('<int:g_id>/', views.group, name='group'),
]

__all__ = ['app_name', 'urlpatterns']
