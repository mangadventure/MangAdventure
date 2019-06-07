from django.views.decorators.vary import vary_on_headers
from django.utils.log import log_response
from django.http import JsonResponse
from functools import wraps


class JsonError(JsonResponse):
    def __init__(self, message, status=500, **kwargs):
        data = {'error': message, 'status': status}
        kwargs.setdefault('status', status)
        super(JsonError, self).__init__(data, **kwargs)


def require_methods_api(allowed_methods=('GET', 'HEAD')):
    """
    Decorator to make an API view only accept particular request methods.
    Based on :func:`~django.views.decorators.http.require_http_request`.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method not in allowed_methods:
                response = JsonError('Method not allowed', 429)
                response['Allow'] = ', '.join(allowed_methods)
                log_response(
                    'Method Not Allowed (%s): %s',
                    request.method, request.path,
                    response=response, request=request,
                )
                return response
            return func(request, *args, **kwargs)
        return (vary_on_headers('Allow'))(inner)
    return decorator


__all__ = ['require_methods_api', 'JsonError', 'JsonResponse']

