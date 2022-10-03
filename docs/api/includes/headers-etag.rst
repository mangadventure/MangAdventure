Request headers
~~~~~~~~~~~~~~~

* `If-None-Match <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-None-Match>`_:
  Send a conditional request checking the ``ETag`` header.

Response headers
~~~~~~~~~~~~~~~~

* `Date <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Date>`_:
  The date of the request.
* `Server <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Server>`_:
  Information regarding the server.
* `Content-Type <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type>`_:
  The content type of the response. (always `application/json <https://www.iana.org/assignments/media-types/application/json>`_)
* `ETag <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag>`_:
  The version identifier of the resource. Useful for caching responses.
* `Content-Length <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Length>`_:
  The size of the response body in bytes.
