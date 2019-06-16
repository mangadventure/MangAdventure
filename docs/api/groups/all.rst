All groups
----------

.. py:data:: GET /api/v1/groups

Retrieve the info of each group.

Example request
^^^^^^^^^^^^^^^

.. sourcecode:: shell

   curl -i http://example.com/api/v1/groups \
        -H 'If-None-Match: 2503eb9066af0aaef2274e8a7d158fd7'

.. include:: ../includes/headers-etag.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. sourcecode:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.7.0
   Content-Type: application/json
   ETag: "ee0581f62afb372d5faea0092d674a87"
   X-Frame-Options: SAMEORIGIN
   Content-Length: 286

   [
      {
         "id": 1,
         "name": "Group",
         "description": "An example group",
         "website": "https://example.com",
         "discord": "https://discord.me/examplegroup",
         "twitter": "ExampleGroup",
         "logo": "https://example.com/media/groups/1/logo.png",
         "members": [
            {
               "id": 1,
               "name": "John Doe",
               "roles": ["Leader"],
               "twitter": "JohnDoe_1234",
               "discord": "John Doe#1234"
            },
         ],
         "series": [
            {
               "slug": "some-manga",
               "title": "Some manga",
               "aliases": ["Some mango"]
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

.. include:: ../includes/group.rst

.. include:: ../includes/status.rst
