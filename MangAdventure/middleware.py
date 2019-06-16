from re import MULTILINE, findall, search


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
            link_src = self._get_link_src(link)
            link_as = search(r'as="(.+?)"', link[0])
            if not (link_src is None or link_as is None):
                preload.append('<{}>; as={}; rel=preload'.format(
                    link_src.group(1), link_as.group(1)
                ))

        if preload:
            response['Link'] = ', '.join(preload)
        return response

    def _get_link_src(self, link):
        return search(
            r'href="(.+?)"' if link[1] == 'link'
            else r'src="(.+?)"', link[0]
        )


__all__ = ['XPBMiddleware', 'PreloadMiddleware']
