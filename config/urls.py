from django.contrib.flatpages.views import flatpage

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

try:
    from csp.decorators import csp_update

    # Allow custom styles & images in info pages
    @csp_update(style_src="'unsafe-inline'", img_src="https:")
    def info_page(req, **kwargs): return flatpage(req, **kwargs)
except ImportError:
    info_page = flatpage

urlpatterns = [
    url(r'^info/$', info_page, {'url': '/info/'}, name='info'),
    url(r'^privacy/$', info_page, {'url': '/privacy/'}, name='privacy'),
]
