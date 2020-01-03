"""The root URLconf."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import contribute, index, opensearch, robots, search

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
    path('robots.txt', robots, name='robots')
]

if settings.DEBUG:  # pragma: no cover
    from django.conf.urls.static import static
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    try:
        from debug_toolbar import urls as debug_urls
        urlpatterns.append(path('__debug__/', include(debug_urls)))
    except ImportError:  # pragma: no cover
        pass

#: See :func:`MangAdventure.views.handler400`.
handler400 = 'MangAdventure.views.handler400'

#: See :func:`MangAdventure.views.handler403`.
handler403 = 'MangAdventure.views.handler403'

#: See :func:`MangAdventure.views.handler404`.
handler404 = 'MangAdventure.views.handler404'

#: See :func:`MangAdventure.views.handler500`.
handler500 = 'MangAdventure.views.handler500'

#: See :func:`MangAdventure.views.handler503`.
handler503 = 'MangAdventure.views.handler503'

__all__ = [
    'urlpatterns', 'handler400', 'handler403',
    'handler404', 'handler500', 'handler503'
]
