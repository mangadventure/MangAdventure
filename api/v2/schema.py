"""Schema utilities."""

from re import compile as regex
from typing import Any, Dict, List

from django.utils.encoding import force_str

from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator
from rest_framework.schemas.utils import get_pk_description
from rest_framework.serializers import BaseSerializer


class OpenAPISchema(AutoSchema):
    """Custom OpenAPI schema class."""
    template_regex = regex(r'{([^}]+)}')

    def map_field(self, field: Any) -> Dict:
        # HACK: map serializers to their $refs
        if isinstance(field, BaseSerializer):
            name = field.field_name.rstrip('s').capitalize()
            ref = {'$ref': '#/components/schemas/' + name}
            if hasattr(field, 'child'):
                return {'type': 'array', 'items': ref}
            return ref
        return super().map_field(field)

    def get_path_parameters(self, path: str, method: str) -> List[Dict]:
        parameters = []
        model = getattr(getattr(self.view, 'queryset', None), 'model', None)
        # HACK: parse the path without using uritemplate
        for variable in self.template_regex.findall(path):
            description = ''
            schema = {'type': 'string'}
            if variable == 'id':
                schema['type'] = 'integer'
            elif variable == 'slug':
                schema['pattern'] = '^[-a-zA-Z0-9_]+$'
            if model is not None:
                field = model._meta.get_field(variable)
                if field is not None:
                    if field.primary_key:
                        description = get_pk_description(model, field)
                    else:
                        description = force_str(field.help_text)
            parameters.append({
                'name': variable,
                'in': 'path',
                'required': True,
                'description': description,
                'schema': schema
            })
        return parameters


class OpenAPISchemaGenerator(SchemaGenerator):
    """Custom OpenAPI generator class."""
    def get_info(self) -> Dict:
        info = super().get_info()
        info['contact'] = {
            'name': 'API Support',
            'url': 'https://github.com/mangadventure/MangAdventure/issues'
        }
        return info

    def get_schema(self, *args, **kwargs) -> Dict:
        from django.conf import settings
        from django.contrib.sites.models import Site

        schema = super().get_schema(*args, **kwargs)
        proto = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        schema.update({
            'servers': [
                {'url': f'{proto}://{site}/api/v2'} for site
                in Site.objects.values_list('domain', flat=True)
            ],
            'externalDocs': {
                'url': 'https://mangadventure.readthedocs.io/',
                'description': 'Documentation'
            },
            'security': ({'ApiKeyHeader': ()}, {'ApiKeyParam': ()})
        })
        schema['components']['securitySchemes'] = {
            'ApiKeyHeader': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-API-Key'
            },
            'ApiKeyParam': {
                'type': 'apiKey',
                'in': 'query',
                'name': 'api_key'
            }
        }
        return schema

    def coerce_path(self, *args) -> str:
        # HACK: strip /api/v2 from the path
        return super().coerce_path(*args)[7:]


__all__ = ['OpenAPISchema', 'OpenAPISchemaGenerator']
