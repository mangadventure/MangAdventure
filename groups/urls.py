"""The URLconf of the groups app."""

from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.decorators.cache import cache_control

from . import feeds, sitemaps, views

#: The URL namespace of the groups app.
app_name = 'groups'

_sitemaps = {
    'template_name': 'image-sitemap.xml',
    'sitemaps': {'groups': sitemaps.GroupSitemap}
}

_sitemap = cache_control(max_age=86400, must_revalidate=True)(sitemap)

#: The URL patterns of the groups app.
urlpatterns = [
    path('', views.all_groups, name='all_groups'),
    path('<int:g_id>/', views.group, name='group'),
    path('<int:g_id>.atom', feeds.GroupAtom(), name='group.atom'),
    path('<int:g_id>.rss', feeds.GroupRSS(), name='group.rss'),
    path('<section>-sitemap.xml', _sitemap, _sitemaps, name='sitemap.xml'),
]

__all__ = ['app_name', 'urlpatterns']
