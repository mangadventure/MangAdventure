"""Schema utilities."""

from __future__ import annotations

from re import compile as regex
from typing import TYPE_CHECKING, Any, Dict, List

from django.utils.encoding import force_str

from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator
from rest_framework.schemas.utils import get_pk_description
from rest_framework.serializers import (
    BaseSerializer, PrimaryKeyRelatedField, SlugRelatedField
)

if TYPE_CHECKING:  # pragma: no cover
    from rest_framework.request import Request


class OpenAPISchema(AutoSchema):
    """Custom OpenAPI schema class."""
    header_regex = regex(r'^\* [a-z]+:')
    variable_regex = regex(r'{([^}]+)}')

    def map_field(self, field: Any) -> Dict:
        # map serializers to their $refs
        if isinstance(field, BaseSerializer):
            name = self.get_component_name(field)
            ref = self._get_reference(name)  # type: ignore
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
                'cover': {'type': 'string', 'format': 'uri', 'default': ''},
                'original_url': {'type': 'string', 'format': 'uri'},
                'description': {'type': 'string', 'default': ''},
                'author': {'type': 'string', 'default': ''},
                'artist': {'type': 'string', 'default': ''},
                'alt_titles': {
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                'metadata': {
                    'type': 'array',
                    'uniqueItems': True,
                    'items': {
                        'type': 'array',
                        'minItems': 2,
                        'maxItems': 2,
                        'items': {'type': 'string'}
                    }
                },
                'chapters': {
                    'type': 'object',
                    'additionalProperties': {
                        'type': 'object',
                        'properties': {
                            'title': {'type': 'string'},
                            'volume': {
                                'type': 'string',
                                'format': 'uint32',
                                'default': '0'
                            },
                            'number': {
                                'type': 'string',
                                'format': 'float',
                                'default': '0'
                            },
                            'groups': {
                                'type': 'object',
                                'minProperties': 1,
                                'maxProperties': 1,
                                'additionalProperties': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'string',
                                        'format': 'uri'
                                    }
                                }
                            },
                            'last_updated': {
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
        # deprecate the /pages path
        if path == '/pages' and method == 'GET':
            op['deprecated'] = True
            op['description'] = (
                '**Use [`/chapters/{id}/pages`]'
                '(#get-/chapters/-id-/pages) instead.**\n\n'
                'Third-party apps must set `track=true`'
                ' to properly increment chapter views.'
            )
        # describe when to track chapter views
        if path == '/chapters/{id}/pages':
            op['description'] = (
                'Third-party apps must set `track=true`'
                ' to properly increment chapter views.'
            )
        # note that Cubari support is experimental
        if path == '/cubari/{slug}':
            op['x-badges'] = [{'color': 'red', 'label': 'Experimental'}]
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
        return self.view.action in ('list', 'chapters', 'pages')

    def get_component_name(self, serializer: BaseSerializer) -> str:
        # HACK: manually set custom action components
        if self.view.action == 'chapters':
            self.view.action = 'list'
            return 'Chapter'
        if self.view.action == 'pages':
            self.view.action = 'list'
            return 'Page'
        return super().get_component_name(serializer)

    def get_responses(self, path: str, method: str) -> Dict[str, Any]:
        responses = super().get_responses(path, method)
        licensed_endpoints = (
            '/series/{slug}/chapters', '/cubari/{slug}',
            '/chapters/{id}', '/chapters/{id}/pages'
        )
        # add 451 response to certain endpoints
        if method == 'GET' and path in licensed_endpoints:
            responses['451'] = {'description': '**The series is licensed.**'}
        return responses


class OpenAPISchemaGenerator(SchemaGenerator):
    """Custom OpenAPI generator class."""

    def get_schema(self, request: Request, public: bool = False) -> Dict:
        from django.contrib.sites.models import Site

        # TODO: use dict union (Py3.9+)
        # add "servers", "externalDocs", "security", "tags" to the main schema
        (schema := super().get_schema(request, public)).update({
            'servers': [
                {'url': f'{request.scheme}://{site}/api/v2'} for site
                in Site.objects.values_list('domain', flat=True)
            ],
            'externalDocs': {
                'url': 'https://mangadventure.readthedocs.io/',
                'description': 'Documentation'
            },
            'security': [{'ApiKeyHeader': []}, {'ApiKeyParam': []}],
            'tags': [
                {'name': 'series'},
                {'name': 'chapters'},
                {'name': 'categories'},
                {'name': 'pages'},
                {'name': 'artists'},
                {'name': 'authors'},
                {'name': 'cubari'},
                {'name': 'groups'},
                {'name': 'members'},
                {'name': 'bookmarks'},
                {'name': 'profile'},
                {'name': 'token'},
            ]
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
        # add "contact" to the info schema
        schema['info']['contact'] = {  # type: ignore
            'name': 'API Support',
            'url': 'https://github.com/mangadventure/MangAdventure/issues'
        }
        return schema  # type: ignore

    def coerce_path(self, *args) -> str:
        # strip /api/v2 from the path
        return super().coerce_path(*args)[7:]


__all__ = ['OpenAPISchema', 'OpenAPISchemaGenerator']
