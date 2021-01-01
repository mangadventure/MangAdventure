"""Template tags used by the flatpage template."""

from typing import TYPE_CHECKING

from django.template.defaultfilters import register

from MangAdventure.jsonld import breadcrumbs

from .custom_tags import jsonld

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.flatpages.models import FlatPage
    from django.http import HttpRequest


@register.filter
def breadcrumbs_ld(request: 'HttpRequest', page: 'FlatPage') -> str:
    """
    Create a JSON-LD ``<script>`` with the page's breadcrumbs.

    :param request: The original request.
    :param page: A :class:`FlatPage` object instance.

    :return: An HTML script tag.
    """
    uri = request.build_absolute_uri(page.url)
    crumbs = breadcrumbs([(page.title, uri)])
    return jsonld(crumbs, 'breadcrumbs')


__all__ = ['breadcrumbs_ld']
