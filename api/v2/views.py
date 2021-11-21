"""The custom views of the api.v2 app."""

from typing import TYPE_CHECKING

from django.http import HttpResponsePermanentRedirect
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
        title='MangAdventure API', renderer_classes=[JSONOpenAPIRenderer],
        generator_class=OpenAPISchemaGenerator, public=True, version='2.0'
    ))
)


def redoc_redirect(request: 'HttpRequest') -> HttpResponsePermanentRedirect:
    """Redirect to the ReDoc demo with our schema."""
    url = request.build_absolute_uri(reverse('api:v2:schema'))
    return HttpResponsePermanentRedirect(
        'https://redocly.github.io/redoc/?nocors&url=' + url
    )


def swagger_redirect(request: 'HttpRequest') -> HttpResponsePermanentRedirect:
    """Redirect to the Swagger generator with our schema."""
    url = request.build_absolute_uri(reverse('api:v2:schema'))
    return HttpResponsePermanentRedirect(
        'https://generator.swagger.io/?url=' + url
    )


__all__ = ['openapi', 'redoc_redirect', 'swagger_redirect']
