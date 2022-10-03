Single author
-------------

.. py:data:: GET /api/v1/authors/:id

Retrieve the info of a certain author.

Request parameters
^^^^^^^^^^^^^^^^^^

* **id** (*int*) - The author's ID.

Example request
^^^^^^^^^^^^^^^

.. code-block:: bash

   curl -i http://example.com/api/v1/authors/1 \
        -H 'If-None-Match: cf62b5e432293fc2b7cf32d5f100d415'

.. include:: ../includes/headers-etag.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. code-block:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.8.13
   Content-Type: application/json
   ETag: "03785faa8c59138c6c16155f51f53bba"
   Content-Length: 141

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


.. include:: ../includes/headers-etag.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is a JSON object which contains the following:

* **id** (*int*) - The ID of the author.
* **name** (*string*) - The name of the author.
* **aliases** (*array of string*) - The author's other names.
* **series** (*array of object*) - The author's series.
  Each object contains the following:

   * **slug** (*slug*) - The slug of the series.
   * **title** (*string*) - The title of the series.
   * **aliases** (*array of string*) - Other names for the series.

.. include:: ../includes/status.rst

* `404 Not Found <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404>`_
  - The requested author doesn't exist.
* `400 Bad Request <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400>`_
  - The id parameter was invalid.
