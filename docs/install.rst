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

First, install the following prerequisites:

* `Python <https://www.python.org/downloads/>`_
* `pip <https://pip.pypa.io/en/stable/installing/>`_
* `virtualenv <https://virtualenv.pypa.io/en/latest/installation/>`_

Afterwards, set up a virtualenv for MangAdventure with the following commands:

.. code-block:: shell

   # This will install a virtualenv under /var/www/my-site.com/
   python -m virtualenv /var/www/my-site.com/

   # This will activate the virtualenv
   source /var/www/my-site.com/bin/activate

Finally, install MangAdventure inside the activated virtualenv:

.. code-block:: shell

   pip install -e git+https://github.com/mangadventure/MangAdventure@v0.5.0#egg=MangAdventure

Configure the settings
^^^^^^^^^^^^^^^^^^^^^^

Before proceeding, there are some settings you will need to configure.
The following command will open a text editor for you to do so:

.. code-block:: shell

   mangadventure configure

You can also specify the editor to use:

.. code-block:: shell

   mangadventure configure --editor /usr/bin/emacs

Create the database
^^^^^^^^^^^^^^^^^^^

This command will create an SQLite database for your site. If it fails,
you might need to install `SQLite <https://www.sqlite.org/index.html>`_.

.. code-block:: shell

   mangadventure migrate

Collect the static files
^^^^^^^^^^^^^^^^^^^^^^^^

These commands will compile and collect the static files (CSS, JS, etc).

.. code-block:: shell

   mangadventure compilestatic
   mangadventure collectstatic --noinput

Create an administrator account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will be prompted for a name, email, and password.
This account is needed to access the ``/admin`` page.
You can create multiple administrator accounts.

.. code-block:: shell

   mangadventure createsuperuser


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

* Visit your site's phpMyAdmin page.
* Click on your FoolSlide2 database.
* Go to the ``Export`` tab.
* In ``Format:`` select ``XML`` and click ``Go``.
* Save the generated file somewhere and copy its path.

Next, import the data into MangAdventure:

* Replace ``{root}`` with the path to your FoolSlide2 installation.
* Replace ``{data}`` with the path to the XML file you exported.

.. code-block:: shell

   mangadventure fs2import {root} {data}

Set up the server
^^^^^^^^^^^^^^^^^

To set up the server you will need Apache, Nginx,
or any other web server that supports Django.
Make sure the user running the web server and ``uwsgi``
has the necessary permissions to access all the relevant files.
Also, create the ``media`` and ``log`` directories
beforehand to avoid possible permission errors.

Apache example
~~~~~~~~~~~~~~

Apache requires `mod_wsgi <https://modwsgi.rtfd.io/en/latest/>`_.

.. literalinclude:: examples/apache.conf
   :language: apache
   :end-before: # vim

Nginx example
~~~~~~~~~~~~~

Nginx requires `uwsgi <https://uwsgi-docs.rtfd.io/en/latest/>`_.

.. literalinclude:: examples/nginx.conf
   :language: nginx
   :end-before: # vim

Don't forget to run ``uwsgi`` after setting up the server:

.. code-block:: shell

   uwsgi --socket 127.0.0.1:25432 --chdir /var/www/my-site.com/ --module MangAdventure.wsgi

For more details, check the uWSGI `docs <https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html#deploying-django>`_.

Updating
--------

First, install the latest release from GitHub:

.. code-block:: shell

   # Replace {tag} with the latest release tag from
   # https://github.com/mangadventure/MangAdventure/releases/latest
   pip install -U git+https://github.com/mangadventure/MangAdventure@{tag}#egg=MangAdventure

Then, compile and collect the static files:

.. code-block:: shell

   mangadventure compilestatic
   mangadventure collectstatic --noinput

Finally, update the database:

.. code-block:: shell

   mangadventure migrate

