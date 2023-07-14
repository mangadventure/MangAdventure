"""The URLconf of the config app."""

from importlib.util import find_spec

from django.conf import settings
from django.contrib.flatpages.views import flatpage
from django.urls import include, path
from django.views.decorators.cache import cache_control

info_page = cache_control(public=True, max_age=43200)(flatpage)
if find_spec('csp'):  # pragma: no cover
    from csp.decorators import csp_update
    info_page = csp_update(
        style_src="'unsafe-inline'",
        img_src="https:"
    )(flatpage)

#: The URL patterns of the config app.
urlpatterns = [
    path('info/', info_page, {'url': '/info/'}, name='info'),
    path('privacy/', info_page, {'url': '/privacy/'}, name='privacy'),
]

if settings.DEBUG:  # pragma: no cover
    from django.conf.urls.static import static
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
    if find_spec('debug_toolbar'):
        from debug_toolbar import urls as djdt_urls
        urlpatterns.append(
            path('__debug__/', include(djdt_urls))  # type: ignore
        )

__all__ = ['urlpatterns']
