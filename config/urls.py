from django.contrib.flatpages.views import flatpage

from django.urls import path as url

try:
    from csp.decorators import csp_update

    # Allow custom styles & images in info pages
    info_page = csp_update(
        style_src="'unsafe-inline'", img_src="https:"
    )(flatpage)
except ImportError:
    info_page = flatpage

urlpatterns = [
    url('info/', info_page, {'url': '/info/'}, name='info'),
    url('privacy/', info_page, {'url': '/privacy/'}, name='privacy'),
]
