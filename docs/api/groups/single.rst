Single group
------------

.. py:data:: GET /api/v1/groups/:id

Retrieve the info of a certain group.

Request parameters
^^^^^^^^^^^^^^^^^^

* **id** (*int*) - The group's ID.

Example request
^^^^^^^^^^^^^^^

.. sourcecode:: shell

   curl -i http://example.com/api/v1/groups/1 \
        -H 'If-None-Match: 820727be5a235d089af4ad66ffeae017'

.. include:: ../includes/headers-etag.rst
   :end-before: Response

Example response
^^^^^^^^^^^^^^^^

.. sourcecode:: http

   HTTP/1.1 200 OK
   Date: Tue, 28 Aug 2018 09:35:27 GMT
   Server: WSGIServer/0.2 CPython/3.7.0
   Content-Type: application/json
   ETag: "37fef7866db8e2a0020d2a4ea519fa75"
   X-Frame-Options: SAMEORIGIN
   Content-Length: 284

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

.. include:: ../includes/headers-etag.rst
   :start-line: 6

Response body
~~~~~~~~~~~~~

The response body is a JSON object which contains the following:

.. include:: ../includes/group.rst

.. include:: ../includes/status.rst

* `404 Not Found <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404>`_
  - The requested group doesn't exist.
* `400 Bad Request <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400>`_
  - The id parameter was invalid.
