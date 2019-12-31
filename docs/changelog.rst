Changelog
---------

v0.6.0
^^^^^^

* Dropped support for Python <3.6
* Dropped support for non-ES6 browsers
* Removed ``ColorField``

v0.5.3
^^^^^^

* Fixed page-click navigation
* Added support for CSP report URI
* Added ``nofollow`` to private links
* Added ``noopener`` & ``noreferrer`` to external links
* Added filters, ordering, search, date hierarchy to admin interface
* Added images & more info to change lists in admin interface
* Replaced large/medium/small logos with a single logo
* Replaced ``django-tinymce`` with custom ``TinyMCE`` widget
* Replaced ``django-constance`` with ``.env`` variables
* Removed ``django-static-precompiler`` dependency

v0.5.2
^^^^^^

* Fixed missing fields in series API response
* Fixed ``OSError`` in ``zipfile_validator``
* Added more blocked user agents & image types
* Added ability to search by slug (for Tachiyomi)
* Added ``PreloadMiddleware`` for HTTP/2 push
* Disabled ``XPBMiddleware``
* Disabled autocomplete in password inputs
* Replaced ``JsonVaryAllowResponse`` with ``require_methods_api``
* Replaced logo ``object`` with ``img``
* Moved ``/admin`` page to ``/admin-panel``
* Moved ``redirects`` & ``sites`` admin pages under ``constance``
* Moved configuration to ``.env``
* Removed ``configure`` command

v0.5.1
^^^^^^

* Fixed group addition edge case.
* Fixed chapter cover images not being closed.
* Implemented series bookmarking.
* Added bookmarks feed page.
* Removed permission to add users from admin interface.

v0.5.0
^^^^^^

* Added support for users (registration, login, OAuth, profile, settings)
* Switched to `custom icon font <https://github.com/mangadventure/font>`_
  made with `fontello <http://fontello.com/>`_
  & replaced ``group.png`` with an SVG image
* Improved reader page design
* Fixed thumbnail downsampling for grayscale images
* Moved templates to ``MangAdventure`` directory
  & renamed ``skeleton.html`` to ``layout.html``
* Converted bad bots list to a python file
* Configured autogeneration of a secret key
* Added ``ColorField`` for constance
* Added constance hook to generate ``_variables.scss`` & removed inline SCSS
* Added ``setup.py`` & ``MANIFEST.in`` for setuptools
* Added optional configuration for django-csp
* Compressed tablesort into a single vendored file
* Converted info page to a flatpage with
  `TinyMCE <https://www.tiny.cloud/docs-4x/>`_ editor
  & added privacy policy page
* Added IRC & Reddit links to groups & members
* Removed configuration commands and added a ``configure`` command
  that lets users edit a configuration file with an editor
* Added support for migration from FoolSlide2
* Added `MangaUpdates <https://www.mangaupdates.com/genres.html>`_
  categories fixture
* Made series slugs editable & added a signal to move directories on change
* Added ``contribute.json`` & ``robots.txt``

v0.4.5
^^^^^^

* Added categories to API.
* Added series filtering to API.

v0.4.4
^^^^^^

* Added categories to series page.
* Removed sha256 hashes.
* Removed breadcrumbs.

v0.4.3
^^^^^^

* Added series categories
* Moved ``/api/`` to ``/api/v1/``
* Made site keywords configurable
* Added Google breadcrumbs & description
* Added OpenSearch description
* Added ``noscript`` fallbacks
* Added ``X-Powered-By`` response header
* Improved database queries

v0.4.2
^^^^^^

* Fixed blocked user agents
* Added default group icon file
* Added ``Vary``, ``Allow`` headers to api responses
* Moved inline styles & scripts to separate files
* Replaced ``pluralize`` script with ``count`` checks
* Switched to ``cdnjs`` for all remote scripts and added SRI hash

v0.4.1
^^^^^^

* Converted chapter numbers to float
* Made page number indicator editable
* Made page compression optional
* Added ``Quality Checker`` to roles

v0.4.0
^^^^^^

* Enabled searching for series via the API

v0.3.1
^^^^^^

* Added group info page

v0.3.0
^^^^^^

* Added groups app
* Restructured custom modules
* Added custom model & form fields
* Added browser icons to compatibility.rst

v0.2.2
^^^^^^

* Added search page
* Enabled conditional requests
* Added authors & artists to the API
* Removed obsolete ``no_future_date`` validator
* Configured API URLs to not require a trailing slash
* Converted docs to rst

v0.2.1
^^^^^^

* Compatibility fixes for Python 2
* Added compatibility tables
* Moved index to MangAdventure.urls
* Renamed settings app to config
* Resized series cover to thumbnail size

v0.2.0
^^^^^^

* Added basic API
* Added HTTPS support
* Fixed html meta tags
* More minor fixes

v0.1.0
^^^^^^

* Initial release
