Categories
==========

.. py:data:: GET /api/v1/categories

Retrieve a list of available categories.

Example request
^^^^^^^^^^^^^^^

.. sourcecode:: shell

   curl -i http://example.com/api/v1/categories \
        -H 'If-None-Match: be534a1d37be8db1c3c57177e1305f6c'

.. include:: ../includes/headers-etag.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. sourcecode:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.7.0
   Content-Type: application/json
   Last-Modified: Sun, 26 Aug 2018 16:40:11 GMT
   ETag: "fe35ca7670b351b38c1c1d5e4b1e773d"
   X-Frame-Options: SAMEORIGIN
   Content-Length: 79

   [
     {
       "id": "drama",
       "name": "Drama",
       "description": "Drama"
     }
   ]

.. include:: includes/headers-etag.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is an array of JSON objects. Each object contains the following:

* **id** (*string*) - The ID of the category.
* **name** (*string*) - The name of the category.
* **description** (*string*) - The description of the category.

.. include:: includes/status.rst

