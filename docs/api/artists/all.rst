All artists
-----------

.. py:data:: GET /api/v1/artists

Retrieve the info of each artist.

Example request
^^^^^^^^^^^^^^^

.. sourcecode:: shell

   curl -i http://example.com/api/v1/artists \
        -H 'If-None-Match: cb51bd8357e0c7fba317ee1331d765c4'

.. include:: ../includes/headers-etag.rst
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

.. include:: ../includes/headers-etag.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is an array of JSON objects.
Each object contains the following:

* **id** (*int*) - The ID of the artist.
* **name** (*string*) - The name of the artist.
* **aliases** (*array of string*) - The artist's other names.
* **series** (*array of object*) - The artist's series.
  Each object contains the following:

   * **slug** (*slug*) - The slug of the series.
   * **title** (*string*) - The title of the series.
   * **aliases** (*array of string*) - Other names for the series.

.. include:: ../includes/status.rst

