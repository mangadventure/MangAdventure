from django.contrib import admin
from django.conf import settings
from users.views import user_logout
from .views import index, info, search, opensearch

try:
    from django.urls import include, re_path as url
except ImportError:
    from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^info/$', info, name='info'),
    url(r'^search/$', search, name='search'),
    url(r'^admin/', admin.site.urls),
    url(r'^reader/', include('reader.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^groups/', include('groups.urls')),
    url(r'^opensearch\.xml$', opensearch, name='opensearch'),
    url(r'^accounts/logout/$', user_logout),
    url(r'^accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

handler404 = 'MangAdventure.views.handler404'
handler500 = 'MangAdventure.views.handler500'
handler503 = 'MangAdventure.views.handler503'

