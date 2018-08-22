from django.urls import include, path as url
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url('', include('reader.urls')),
    url('admin/', admin.site.urls),
    url('api/', include('api.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

handler404 = 'MangAdventure.views.handler404'
handler500 = 'MangAdventure.views.handler500'

