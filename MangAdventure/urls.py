from django.contrib import admin
from django.urls import include, path as url

urlpatterns = [
    url('', include('reader.urls')),
    url('admin/', admin.site.urls),
]

handler404 = 'MangAdventure.views.handler404'
handler500 = 'MangAdventure.views.handler500'

