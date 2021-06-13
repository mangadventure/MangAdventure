Installation
------------

.. warning::

   This project is still in an experimental state and may be unstable.
   Proceed at your own risk.

.. note::

   This tutorial assumes you are using Linux and plan on
   installing MangAdventure under ``/var/www/my-site.com/``.
   The instructions are similar for Windows and MacOS.

Install the project
^^^^^^^^^^^^^^^^^^^

First, you will need Python_ (3.6+) and pip_.

.. _Python: https://www.python.org/downloads/

.. _pip: https://pip.pypa.io/en/stable/installing/

Then, set up a virtualenv for MangAdventure with the following commands:

.. code-block:: shell

   # This will install a virtualenv under /var/www/my-site.com/
   python3 -m venv /var/www/my-site.com/

   # This will activate the virtualenv
   source /var/www/my-site.com/bin/activate

   # You may need to install wheel manually
   pip install wheel

Finally, install MangAdventure inside the activated virtualenv:

.. code-block:: shell

   pip install -e "git+https://github.com/mangadventure/MangAdventure@v0.7.3#egg=mangadventure"

MangAdventure also provides the following extras:

* ``mysql``: `MySQL database support`_
* ``pgsql``: `PostgreSQL database support`_
* ``csp``: `Content-Security-Policy headers`_
* ``sentry``: `Sentry error reporting`_
* ``uwsgi``: `uWSGI application server`_

For example, you can install ``csp`` & ``uwsgi`` like so:

.. code-block:: shell

   pip install -e "git+https://github.com/mangadventure/MangAdventure@v0.7.3#egg=mangadventure[csp,uwsgi]"

.. _MySQL database support:
   https://mysql.com/

.. _PostgreSQL database support:
   https://www.postgresql.org

.. _Content-Security-Policy headers:
   https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP

.. _Sentry error reporting:
   https://sentry.io/for/django/

.. _uWSGI application server:
   https://uwsgi-docs.readthedocs.io/en/latest/index.html

Configure the settings
^^^^^^^^^^^^^^^^^^^^^^

Before proceeding, there are some settings you will need to configure.
To configure them, copy the ``.env.example`` file to ``.env`` and edit it.

You can also override the styling of the site by writing some SCSS
(or regular CSS) in the ``static/extra/style.scss`` file.

Create the database
^^^^^^^^^^^^^^^^^^^

This command will set up the database for your site.

.. code-block:: shell

   mangadventure migrate

Collect the static files
^^^^^^^^^^^^^^^^^^^^^^^^

This command will collect the static files into ``static/``.


.. code-block:: shell

   mangadventure collectstatic

Create an administrator account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will be prompted for a name, email, and password.
This account is needed to access the ``/admin-panel/`` page.
You can create multiple administrator accounts.

.. code-block:: shell

   mangadventure createsuperuser

Load Categories
^^^^^^^^^^^^^^^

If you want to load an initial set of manga categories imported from
`MangaUpdates <https://www.mangaupdates.com/genres.html>`_, run this command:

.. code-block:: shell

   mangadventure loaddata categories

Migrate from FoolSlide2
^^^^^^^^^^^^^^^^^^^^^^^

| You can import your data from a FoolSlide2 installation.
| If you weren't using FoolSlide2 before, feel free to
   skip to the `next section <#set-up-the-server>`_.

.. admonition:: Limitations
   :class: warning

   * Series will be imported without authors & artists.
   * Users & team members will not be imported.
   * Chapters with multiple teams will be imported without the teams.
   * Languages are not yet supported and thus cannot be imported.
   * This has only been tested with FoolSlide2 v2.3.3 using a MySQL database.

First, export the data from FoolSlide2:

* Visit your site's ``phpMyAdmin`` page.
* Click on your FoolSlide2 database.
* Go to the ``Export`` tab.
* In ``Format:`` select ``XML`` and click ``Go``.
* Save the generated file somewhere and copy its path.

Next, import the data into MangAdventure:

* Replace ``{root}`` with the path to your FoolSlide2 installation.
* Replace ``{data}`` with the path to the XML file you exported.

.. code-block:: shell

   mangadventure fs2import "{root}" "{data}"

Set up the server
^^^^^^^^^^^^^^^^^

| To set up the server you will need Apache, Nginx,
   or any other web server that supports Django.
| Make sure the user running the web server and ``uwsgi``
   has the necessary permissions to access all the relevant files.
| Also, create the ``media`` and ``log`` directories
   beforehand to avoid possible permission errors.
| Lastly, don't forget to run ``uwsgi`` after setting up the server:
| (For more details, check the `uWSGI docs`_.)

.. code-block:: shell

   uwsgi --socket "127.0.0.1:25432" --chdir "/var/www/my-site.com" --module "MangAdventure.wsgi"

.. _uWSGI docs:
   https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html#deploying-django

Apache example
~~~~~~~~~~~~~~

Apache requires `mod_uwsgi`_.

.. literalinclude:: examples/apache.conf
   :language: apache
   :end-before: # vim

.. _mod_uwsgi:
   https://uwsgi-docs.readthedocs.io/en/latest/Apache.html

Nginx example
~~~~~~~~~~~~~

Nginx requires `uwsgi`_.

.. literalinclude:: examples/nginx.conf
   :language: nginx
   :end-before: # vim

.. _uwsgi:
   https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html

Updating
--------

| First, install the latest release from GitHub:
| (Replace ``{tag}`` with the latest `release tag`_.)

.. code-block:: shell

   # Don't forget to activate the virtualenv
   source /var/www/my-site.com/bin/activate

   pip install -U -e "git+https://github.com/mangadventure/MangAdventure@{tag}#egg=MangAdventure"

Then, check ``.env.example`` for new variables. If there are any, set them in ``.env``.

Finally, update the database:

.. code-block:: shell

   mangadventure migrate

.. _release tag:
   https://github.com/mangadventure/MangAdventure/releases/latest
