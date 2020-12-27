"""Convenience classes and functions for API responses."""

from functools import wraps
from typing import TYPE_CHECKING, Tuple

from django.http import JsonResponse
from django.utils.log import log_response
from django.views.decorators.vary import vary_on_headers

if TYPE_CHECKING:  # pragma: no cover
    from typing import Callable  # isort:skip
    from django.http import HttpRequest  # isort:skip


class JsonError(JsonResponse):
    """
    A JSON-formatted error response.

    :param message: The error message of the response.
    :param status: The HTTP status of the response.
    """
    def __init__(self, message: str, status: int = 500, **kwargs):
        data = {'error': message, 'status': status}
        kwargs.setdefault('status', status)
        super(JsonError, self).__init__(data, **kwargs)


def require_methods_api(allowed_methods: Tuple[str, ...] =
                        ('GET', 'HEAD')) -> 'Callable':
    """
    | Decorator to make an API view only accept particular request methods.
    | Based on :func:`django.views.decorators.http.require_http_request`.

    :param allowed_methods: The allowed request methods.
    """
    def decorator(func: 'Callable') -> 'Callable':
        @wraps(func)
        def inner(request: 'HttpRequest', *args, **kwargs) -> JsonError:
            if request.method not in allowed_methods:
                response = JsonError('Method not allowed', 405)
                response['Allow'] = ', '.join(allowed_methods)
                log_response(
                    'Method Not Allowed (%s): %s',
                    request.method, request.path,
                    response=response, request=request,
                )
                return response
            return func(request, *args, **kwargs)
        return vary_on_headers('Allow')(inner)
    return decorator


__all__ = ['require_methods_api', 'JsonError']
