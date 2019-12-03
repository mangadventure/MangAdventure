from re import MULTILINE, findall, search

from django.middleware.common import CommonMiddleware


class BaseMiddleware(CommonMiddleware):
    def __call__(self, request):
        if request.path == '/robots.txt':
            return self.get_response(request)
        return super(BaseMiddleware, self).__call__(request)

    def should_redirect_with_slash(self, request):
        if request.path.startswith('/api'):
            return False
        return super(BaseMiddleware, self).should_redirect_with_slash(request)


class XPBMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('X-Powered-By', 'MangAdventure')
        return response


class PreloadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'text/html' not in response['Content-Type']:
            return response

        preload = []
        pattern = r'(<(link|script|img)[^>]+?' + \
            r'rel="[^>]*?preload[^>]*?"[^>]*?/?>)'
        content = str(response.content)

        for link in findall(pattern, content, MULTILINE):
            src = self._get_link_src(link)
            as_ = search(r'as="(.+?)"', link[0])
            if src and as_:
                preload.append(
                    f'<{src.group(1)}>; as={as_.group(1)}; rel=preload'
                )

        if preload:
            response['Link'] = ', '.join(preload)
        return response

    def _get_link_src(self, link):
        return search(
            r'href="(.+?)"' if link[1] == 'link'
            else r'src="(.+?)"', link[0]
        )


__all__ = ['BaseMiddleware', 'XPBMiddleware', 'PreloadMiddleware']
