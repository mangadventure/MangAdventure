from django.http import JsonResponse


class JsonVaryAllowResponse(JsonResponse):
    def __init__(self, *args, **kwargs):
        vary = kwargs.pop('vary', 'Allow')
        status = kwargs.get('status', 200)
        if(status == 405):
            allow = kwargs.pop('allow', 'GET, HEAD')
        super(JsonVaryAllowResponse, self).__init__(*args, **kwargs)
        self.setdefault('Vary', vary)
        if(status == 405):
            self.setdefault('Allow', allow)


class JsonError(JsonVaryAllowResponse):
    def __init__(self, message, status=500, **kwargs):
        data = {'error': message, 'status': status}
        kwargs.setdefault('status', status)
        super(JsonError, self).__init__(data, **kwargs)


__all__ = ['JsonVaryAllowResponse', 'JsonError']

