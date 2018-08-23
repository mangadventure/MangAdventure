from django.contrib import admin
from django.conf import settings
from .views import index

try:
    from django.urls import include, re_path as url
except ImportError:
    from django.conf.urls import include, url

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^reader/', include('reader.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

handler404 = 'MangAdventure.views.handler404'
handler500 = 'MangAdventure.views.handler500'

