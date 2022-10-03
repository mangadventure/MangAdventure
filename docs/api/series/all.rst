All series
----------

.. py:data:: GET /api/v1/series

Retrieve the info of every series.

Example request
^^^^^^^^^^^^^^^

.. code-block:: bash

   curl -i http://example.com/api/v1/series \
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
   Last-Modified: Sun, 26 Aug 2018 16:40:11 GMT
   ETag: "2ce26c7f5182ce4aa4793147627b2a96"
   Content-Length: 510

   [
     {
       "slug": "some-manga",
       "title": "Some Manga",
       "aliases": [
         "Some Mango"
       ],
       "url": "https://example.com/reader/some-manga/",
       "description": "Some description.",
       "authors": [
         ["John Doe", "Johnnie Doe"],
         ["Jack Doe"]
       ],
       "artists": [
         ["Jane Doe"]
       ],
       "categories": [
         {
           "name": "Drama",
           "description": "Drama"
         }
       ],
       "cover": "http://example.com/media/series/some-manga/cover.jpg",
       "completed": false,
       "volumes": {
         "1": {
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
             "pages_root": "http://example.com/media/series/some-manga/1/0/",
             "date": "Sun, 26 Aug 2018 16:14:52 GMT",
             "final": false
           }
         }
       }
     }
   ]


.. include:: ../includes/headers-modified.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is an array of JSON objects.
Each object contains the following:

.. include:: ../includes/series.rst

.. include:: ../includes/chapter.rst
   :start-after: indented

.. include:: ../includes/status.rst
