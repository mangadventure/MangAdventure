class XPBMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Powered-By'] = 'MangAdventure'
        return response


__all__ = ['XPBMiddleware']

