Volume
------

.. py:data:: GET /api/v1/series/:slug/:volume

Retrieve all chapters of a volume.

Request parameters
^^^^^^^^^^^^^^^^^^

* **slug** (*string*) - The slug of the series.
* **volume** (*int*) - A volume of the series.

Example request
^^^^^^^^^^^^^^^

.. code-block:: bash

   curl -i http://example.com/api/v1/series/some-manga/1 \
        -H 'If-Modified-Since: Fri, 24 Aug 2018 12:48:01 GMT'

.. include:: ../includes/headers-modified.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. code-block:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.8.13
   Content-Type: application/json
   Last-Modified: Sun, 26 Aug 2018 16:14:52 GMT
   ETag: "88bc064c71f4d4e925c6725de3077fd4"
   Content-Length: 187

   {
     "0": {
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
   }

.. include:: ../includes/headers-modified.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is a JSON object.
The key of each object is the chapter number.
The value is an object containing the info of the chapter:

.. include:: ../includes/chapter.rst
   :end-before: ..

.. include:: ../includes/status.rst

* `404 Not Found <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404>`_
  - The requested series or volume doesn't exist.
* `400 Bad Request <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400>`_
  - The volume parameter was invalid.
