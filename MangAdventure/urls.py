"""The root URLconf."""

from django.contrib import admin
from django.urls import include, path

from reader import feeds

from .views import contribute, index, manifest, opensearch, robots, search

#: The main URL patterns.
urlpatterns = [
    path('', index, name='index'),
    path('', include('config.urls')),
    path('search/', search, name='search'),
    path('admin-panel/', admin.site.urls),
    path('reader/', include('reader.urls')),
    path('api/', include('api.urls')),
    path('groups/', include('groups.urls')),
    path('user/', include('users.urls')),
    path('opensearch.xml', opensearch, name='opensearch'),
    path('contribute.json', contribute, name='contribute'),
    path('manifest.webmanifest', manifest, name='manifest'),
    path('robots.txt', robots, name='robots'),
    path('releases.atom', feeds.ReleasesAtom(), name='releases.atom'),
    path('releases.rss', feeds.ReleasesRSS(), name='releases.rss'),
    path('library.atom', feeds.LibraryAtom(), name='library.atom'),
    path('library.rss', feeds.LibraryAtom(), name='library.rss'),
]


#: See :func:`MangAdventure.views.handler400`.
handler400 = 'MangAdventure.views.handler400'

#: See :func:`MangAdventure.views.handler403`.
handler403 = 'MangAdventure.views.handler403'

#: See :func:`MangAdventure.views.handler404`.
handler404 = 'MangAdventure.views.handler404'

#: See :func:`MangAdventure.views.handler500`.
handler500 = 'MangAdventure.views.handler500'

__all__ = [
    'urlpatterns', 'handler400',
    'handler403', 'handler404', 'handler500',
]
