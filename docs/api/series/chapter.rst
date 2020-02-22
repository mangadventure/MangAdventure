Chapter
-------

.. py:data:: GET /api/v1/series/:slug/:volume/:chapter


Retrieve a certain chapter of a volume.

Request parameters
^^^^^^^^^^^^^^^^^^

* **slug** (*string*) - The slug of the series.
* **volume** (*int*) - A volume of the series.
* **chapter** (*int*) - A chapter of the volume.

Example request
^^^^^^^^^^^^^^^

.. sourcecode:: shell

   curl -i http://example.com/api/v1/series/some-manga/1/0 \
        -H 'If-Modified-Since: Fri, 24 Aug 2018 12:48:01 GMT'

.. include:: ../includes/headers-modified.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. sourcecode:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.7.0
   Content-Type: application/json
   Last-Modified: Sun, 26 Aug 2018 16:14:52 GMT
   ETag: "11b9df2f0904dc4f1b2dfaa7d7419bbc"
   X-Frame-Options: SAMEORIGIN
   Content-Length: 181

   {
     "url": "http://example.com/reader/some-manga/1/0/",
     "title": "Prologue",
     "full_title": "Vol. 1, Ch. 0: Prologue",
     "pages_list": [
       "001.jpg",
       "002.jpg",
       "003.jpg",
       "004.jpg"
     ],
     "pages_root": "http://example.com/media/some-manga/1/0/",
     "date": "Sun, 26 Aug 2018 16:14:52 GMT",
     "final": false
   }

.. include:: ../includes/headers-modified.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is a JSON object containing the following:

.. include:: ../includes/chapter.rst
   :end-before: ..

.. include:: ../includes/status.rst

* `404 Not Found <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404>`_
  - The requested series, volume, or chapter doesn't exist.
* `400 Bad Request <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400>`_
  - The volume or chapter parameter was invalid.
