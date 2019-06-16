All authors
-----------

.. py:data:: GET /api/v1/authors

Retrieve the info of each author.

Example request
^^^^^^^^^^^^^^^

.. sourcecode:: shell

   curl -i http://example.com/api/v1/authors \
        -H 'If-None-Match: f2e17505f242cfbcd13496c3bd05f223'

.. include:: ../includes/headers-etag.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. sourcecode:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.7.0
   Content-Type: application/json
   ETag: "5c67e7ccb7f5e711431e81053dad33bb"
   X-Frame-Options: SAMEORIGIN
   Content-Length: 143

   [
     {
       "id": 1,
       "name": "John Doe",
       "aliases": ["Johnnie Doe"],
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

* **id** (*int*) - The ID of the author.
* **name** (*string*) - The name of the author.
* **aliases** (*array of string*) - The author's other names.
* **series** (*array of object*) - The author's series.
  Each object contains the following:

   * **slug** (*slug*) - The slug of the series.
   * **title** (*string*) - The title of the series.
   * **aliases** (*array of string*) - Other names for the series.

.. include:: ../includes/status.rst
