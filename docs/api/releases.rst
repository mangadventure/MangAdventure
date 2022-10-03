Releases
========

.. py:data:: GET /api/v1/releases

Retrieve the latest release of each series.

Example request
^^^^^^^^^^^^^^^

.. code-block:: bash

   curl -i http://example.com/api/v1/releases \
        -H 'If-Modified-Since: Fri, 24 Aug 2018 12:48:01 GMT'

.. include:: includes/headers-modified.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. code-block:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.8.13
   Content-Type: application/json
   Last-Modified: Sun, 26 Aug 2018 16:40:11 GMT
   ETag: "6fd721cb9531502d4c52f0f3ebc34f22"
   Content-Length: 254

   [
     {
       "slug": "some-manga",
       "title": "Some Manga",
       "url": "http://example.com/reader/some-manga/",
       "cover": "http://example.com/media/series/some-manga/cover.jpg",
       "latest_chapter": {
         "title": "Prologue",
         "volume": 1,
         "number": 0,
         "date": "Sun, 26 Aug 2018 16:14:52 GMT"
       }
     },
   ]

.. include:: includes/headers-modified.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is an array of JSON objects.
Each object contains the following:

* **slug** (*string*) - The slug of the series.
* **title** (*string*) - The title of the series.
* **url** (*string*) - The URL of the series.
* **cover** (*string*) - The URL of the series's cover.
* **latest_chapter** (*object*) - The latest chapter of the series.

   * **title** (*string*) - The title of the chapter.
   * **volume** (*int*) - The volume of the chapter.
   * **number** (*int*) - The number of the chapter.
   * **date** (*string*) - The date the chapter was published.

.. include:: includes/status.rst
