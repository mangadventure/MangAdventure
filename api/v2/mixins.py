"""API mixin classes."""

from functools import wraps
from typing import Callable


class CORSMixin:
    """Mixin that sets CORS headers."""

    #: CORS headers dictionary.
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'X-API-Key',
        'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS'
    }

    @property
    def default_response_headers(self) -> dict:
        allowed_methods = getattr(self, 'allowed_methods', [])
        renderer_classes = getattr(self, 'renderer_classes', [])
        headers = self.cors_headers
        headers['Allow'] = ', '.join(allowed_methods)
        if len(renderer_classes) > 1:
            headers['Vary'] = 'Accept'
        return headers

    @classmethod
    def decorator(cls, func: Callable) -> Callable:
        """Use the CORS headers as a view decorator."""
        @wraps(func)
        def inner(*args, **kwargs):
            response = func(*args, **kwargs)
            # response.headers.update is not available
            for k, v in cls.cors_headers.items():
                response.headers[k] = v
            return response
        return inner


#: The allowed HTTP request methods.
METHODS = ['get', 'post', 'patch', 'delete', 'head', 'options']

__all__ = ['CORSMixin', 'METHODS']
