Request headers
~~~~~~~~~~~~~~~

* `If-Modified-Since <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Modified-Since>`_:
  Send a conditional request checking the ``Last-Modified`` header.

Response headers
~~~~~~~~~~~~~~~~

* `Date <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Date>`_:
  The date of the request.
* `Server <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Server>`_:
  Information regarding the server.
* `Content-Type <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type>`_:
  The content type of the response. (always `application/json <https://www.iana.org/assignments/media-types/application/json>`_)
* `Last-Modified <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified>`_:
  The date the resource was last modified. Useful for caching responses.
* `ETag <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag>`_:
  The version identifier of the resource. Useful for caching responses.
* `Content-Length <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Length>`_:
  The size of the response body in bytes.
