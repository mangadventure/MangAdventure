"""Custom middleware."""

from __future__ import annotations

from re import MULTILINE, findall, search
from typing import TYPE_CHECKING

from django.http import HttpResponse
from django.middleware.common import CommonMiddleware

if TYPE_CHECKING:  # pragma: no cover
    from typing import Callable  # isort:skip
    from django.http import HttpRequest  # isort:skip


class HttpResponseTooEarly(HttpResponse):
    status_code = 425


class BaseMiddleware(CommonMiddleware):
    """``CommonMiddleware`` with custom patches."""

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Patched to allow :const:`blocked user agents
        <MangAdventure.settings.DISALLOWED_USER_AGENTS>`
        to view ``/robots.txt``.

        It also sends a :status:`425` response if
        the :header:`Early-Data` header has been set.

        :param request: The original request.

        :return: The response to the request.
        """
        if request.META.get('HTTP_EARLY_DATA') == '1':
            return HttpResponseTooEarly()
        if request.path == '/robots.txt':
            return self.get_response(request)  # type: ignore
        return super().__call__(request)


class PreloadMiddleware:
    """Middleware that allows for preloading resources."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Add a ``Link`` header with preloadable resources to the response.

        :param request: The original request.

        :return: The response to the request.
        """
        response = self.get_response(request)
        if 'text/html' not in response.get('Content-Type', ''):
            return response

        preload = []
        pattern = (
            r'(<(link|script|img)[^>]+?rel='
            r'"[^>]*?preload[^>]*?"[^>]*?/?>)'
        )
        content = str(response.content)

        for link in findall(pattern, content, MULTILINE):
            src = search(
                r'href="(/.+?)"' if link[1] == 'link'
                else r'src="(/.+?)"', link[0]
            )
            as_ = search(r'as="(.+?)"', link[0])
            if src and as_:
                preload.append(
                    f'<{src.group(1)}>; as={as_.group(1)}; rel=preload'
                )

        if preload:
            response['Link'] = ', '.join(preload)
        return response


__all__ = ['BaseMiddleware', 'PreloadMiddleware']
