Artists
=======

All artists
-----------

.. py:data:: GET /api/artists

Retrieve the info of each artist.

Example request
^^^^^^^^^^^^^^^

.. sourcecode:: shell

   curl -i http://example.com/api/artists \
        -H 'If-None-Match: cb51bd8357e0c7fba317ee1331d765c4'

.. include:: includes/headers-etag.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. sourcecode:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.7.0
   Content-Type: application/json
   ETag: "31b0b177cc7138befc5dd56ae745e313"
   X-Frame-Options: SAMEORIGIN
   Content-Length: 133

   [
     {
       "id": 1,
       "name": "Nemo Nobody",
       "aliases": [],
       "series": [
         {
           "slug": "some-manga",
           "title": "Some Manga",
           "aliases": ["Some Mango"]
         }
       ]
     }
   ]

.. include:: includes/headers-etag.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is an array of JSON objects.
Each object contains the following:

* **id** (*int*) - The ID of the artist.
* **name** (*string*) - The name of the artist.
* **aliases** (*string*) - The artist's other names.
* **series** (*array of object*) - The artist's series.
  Each object contains the following:

   * **slug** (*slug*) - The slug of the series.
   * **title** (*string*) - The title of the series.
   * **aliases** (*array of string*) - Other names for the series.

.. include:: includes/status.rst

Single artist
-------------

.. py:data:: GET /api/artists/:id

Retrieve the info of a certain artist.

Request parameters
^^^^^^^^^^^^^^^^^^

* **id** (*int*) - The artist's ID.

Example request
^^^^^^^^^^^^^^^

.. sourcecode:: shell

   curl -i http://example.com/api/artists/1 \
        -H 'If-None-Match: 7cd7ac5d353b1ee4833b6b1e1cf17705'

.. include:: includes/headers-etag.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. sourcecode:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.7.0
   Content-Type: application/json
   ETag: "3bcf5cf18a6ac3a515878561f5b10395"
   X-Frame-Options: SAMEORIGIN
   Content-Length: 131

   {
     "id": 1,
     "name": "Nemo Nobody",
     "aliases": [],
     "series": [
       {
         "slug": "some-manga",
         "title": "Some Manga",
         "aliases": ["Some Mango"]
       }
     ]
   }


.. include:: includes/headers-etag.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is a JSON object which contains the following:

* **id** (*int*) - The ID of the artist.
* **name** (*string*) - The name of the artist.
* **aliases** (*string*) - The artist's other names.
* **series** (*array of object*) - The artist's series.
  Each object contains the following:

   * **slug** (*slug*) - The slug of the series.
   * **title** (*string*) - The title of the series.
   * **aliases** (*array of string*) - Other names for the series.

.. include:: includes/status.rst

* `404 Not Found <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404>`_
  - The requested artist doesn't exist.
* `400 Bad Request <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400>`_
  - The id parameter was invalid.

