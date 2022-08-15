"""The custom views of the api.v2 app."""

from __future__ import annotations

from importlib.util import find_spec
from typing import TYPE_CHECKING

from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import cache_control

from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view

from .mixins import CORSMixin
from .schema import OpenAPISchemaGenerator

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest

#: The generated OpenAPI schema as a view.
openapi = cache_control(public=True, max_age=1296000, immutable=True)(
    CORSMixin.decorator(get_schema_view(
        title='MangAdventure API', version='2.2',
        generator_class=OpenAPISchemaGenerator, public=True,
        renderer_classes=[JSONOpenAPIRenderer]  # type: ignore
    ))
)


def redoc_redirect(request: HttpRequest) -> HttpResponse:
    """
    Redirect to the ReDoc demo with our schema.

    .. deprecated:: 0.8.2
       Removed in favor of :func:`~api.v2.views.rapidoc`.
    """
    return HttpResponse('Use /api/v2/docs/ instead', status=410)


def swagger_redirect(request: HttpRequest) -> HttpResponse:
    """
    Redirect to the Swagger generator with our schema.

    .. deprecated:: 0.8.2
       Removed in favor of :func:`~api.v2.views.rapidoc`.
    """
    return HttpResponse('Use /api/v2/docs/ instead', status=410)


def _rapidoc(request: HttpRequest) -> HttpResponse:
    """
    View that serves the RapiDoc_ documentation of the site.

    :param request: The original request.

    :return: A response with the rendered ``rapidoc.html`` template.

    .. _RapiDoc: https://mrin9.github.io/RapiDoc/
    """
    return render(request, 'rapidoc.html', {
        'schema': reverse('api:v2:schema'),
    })


if find_spec('csp'):  # pragma: no cover
    from csp.decorators import csp_update
    rapidoc = csp_update(style_src="'unsafe-inline'")(_rapidoc)
else:
    rapidoc = _rapidoc
rapidoc.__doc__ = _rapidoc.__doc__


__all__ = ['openapi', 'redoc_redirect', 'swagger_redirect', 'rapidoc']
