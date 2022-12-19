"""Custom middleware."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponse
from django.middleware.common import CommonMiddleware

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest


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
            return self.get_response(request)
        return super().__call__(request)


__all__ = ['BaseMiddleware']
