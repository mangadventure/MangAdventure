"""Schema utilities."""

from re import compile as regex
from typing import Any, Dict, List

from django.utils.encoding import force_str

from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator
from rest_framework.schemas.utils import get_pk_description
from rest_framework.serializers import (
    BaseSerializer, PrimaryKeyRelatedField, SlugRelatedField
)


class OpenAPISchema(AutoSchema):
    """Custom OpenAPI schema class."""
    header_regex = regex(r'^\* [a-z]+:')
    variable_regex = regex(r'{([^}]+)}')

    def map_field(self, field: Any) -> Dict:
        # map serializers to their $refs
        if isinstance(field, BaseSerializer):
            name = field.field_name.rstrip('s').capitalize()
            ref = {'$ref': '#/components/schemas/' + name}
            if hasattr(field, 'child'):
                return {'type': 'array', 'items': ref}
            return ref
        # fix primary key field type
        if isinstance(field, PrimaryKeyRelatedField):
            return {'type': 'integer'}
        result = super().map_field(field)
        # specify pattern for slug related fields
        if isinstance(field, SlugRelatedField):
            result['pattern'] = '^[-a-zA-Z0-9_]+$'
        # specify format for password fields
        if field.style.get('input_type') == 'password':
            result['format'] = 'password'
        return result

    def map_field_validators(self, field: Any, schema: Dict):
        super().map_field_validators(field, schema)
        # specify format for float fields
        if schema['type'] == 'number':
            schema['format'] = 'float'
        # remove pattern from uri fields
        if schema.get('format') == 'uri':
            schema.pop('pattern', None)

    def map_serializer(self, serializer: BaseSerializer) -> Dict:
        if serializer.__class__.__name__[:6] != 'Cubari':
            return super().map_serializer(serializer)
        # HACK: hard-code Cubari schema as it's too complex
        return {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'description': {'type': 'string', 'default': ''},
                'author': {'type': 'string', 'default': ''},
                'artist': {'type': 'string', 'default': ''},
                'cover': {
                    'type': 'string',
                    'format': 'uri',
                    'default': ''
                },
                'chapters': {
                    'type': 'object',
                    'additionalProperties': {
                        'type': 'object',
                        'properties': {
                            'title': {'type': 'string'},
                            'volume': {
                                'type': 'string',
                                'format': 'uint64',
                                'default': None,
                                'nullable': True
                            },
                            'groups': {
                                'type': 'object',
                                'additionalProperties': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'string',
                                        'format': 'uri'
                                    }
                                }
                            },
                            'latest_update': {
                                'type': 'string',
                                'format': 'uint64',
                                'default': ''
                            }
                        }
                    }
                }
            }
        }

    def get_operation(self, path: str, method: str) -> Dict:
        op = super().get_operation(path, method)
        op['summary'] = op.pop('description', '')
        # fix incorrect plural forms
        if op['operationId'][-2:] == 'ys':
            op['operationId'] = op['operationId'][:-2] + 'ies'
        # disable security for unrestricted operations
        if method == 'GET' and not hasattr(self.view, '_restrict'):
            op['security'] = ()
        elif not self.view.permission_classes:
            op['security'] = ()
        return op

    def get_path_parameters(self, path: str, method: str) -> List[Dict]:
        parameters = []
        model = getattr(getattr(self.view, 'queryset', None), 'model', None)
        # parse the path without depending on uritemplate
        for variable in self.variable_regex.findall(path):
            description = ''
            schema = {'type': 'string'}
            if variable == 'id':
                schema['type'] = 'integer'
            elif variable == 'slug':
                schema['pattern'] = '^[-a-zA-Z0-9_]+$'
                description = 'The slug of the series.'
            if model is not None:
                field = model._meta.get_field(variable)
                if field is not None:
                    if field.primary_key:
                        description = get_pk_description(model, field)
                    elif field.help_text:
                        description = force_str(field.help_text)
            parameters.append({
                'name': variable,
                'in': 'path',
                'required': True,
                'description': description,
                'schema': schema
            })
        return parameters

    def allows_filters(self, path: str, method: str) -> bool:
        if getattr(self.view, 'filter_backends', None) is None:
            return False
        # only allow filters in list endpoints
        return self.view.action == 'list'


class OpenAPISchemaGenerator(SchemaGenerator):
    """Custom OpenAPI generator class."""
    def get_info(self) -> Dict:
        info = super().get_info()
        # add "contact" to the info schema
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
        # add "servers", "externalDocs", "security", "tags" to the main schema
        schema.update({
            'servers': [
                {'url': f'{proto}://{site}/api/v2'} for site
                in Site.objects.values_list('domain', flat=True)
            ],
            'externalDocs': {
                'url': 'https://mangadventure.readthedocs.io/',
                'description': 'Documentation'
            },
            'security': ({'ApiKeyHeader': ()}, {'ApiKeyParam': ()}),
            'tags': (
                {'name': 'series'},
                {'name': 'chapters'},
                {'name': 'categories'},
                {'name': 'pages'},
                {'name': 'artists'},
                {'name': 'authors'},
                {'name': 'cubari'},
                {'name': 'groups'},
                {'name': 'bookmarks'},
                {'name': 'profile'},
                {'name': 'token'},
            )
        })
        # add "securitySchemes" to the components schema
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
