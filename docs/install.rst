Dependencies
------------

* `Python <https://www.python.org/downloads/>`_
* `Django <https://www.djangoproject.com/download/>`_
* `Django Next-Prev <https://pypi.org/project/django-next-prev/>`_
* `Django Constance <https://django-constance.readthedocs.io/en/latest/#installation>`_
* `Django Picklefield <https://pypi.org/project/django-picklefield/>`_
* `Django Static Precompiler <https://django-static-precompiler.readthedocs.io/en/stable/installation.html>`_
* `LibSass <https://sass.github.io/libsass-python/#install>`_
* `Pillow <https://pillow.readthedocs.io/en/latest/installation.html#basic-installation>`_

Installing
----------

.. warning::

   This project is still in an experimental state and may be unstable.
   Proceed at your own risk.

First, install the dependencies. If you already have Python & `pip <https://pip.pypa.io/en/stable/installing/>`_\ , you can install all the required Python modules with:

.. code-block:: shell

   pip install -r requirements.txt

Then, download and unzip the `latest release <https://github.com/evangelos-ch/MangAdventure/releases/>`_ and follow these steps to initialize the site:

Generate a secret key
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   python manage.py generatekey

Configure the site URL
^^^^^^^^^^^^^^^^^^^^^^

Replace ``<URL>`` with the URL of your website.

.. code-block:: shell

   python manage.py configureurl <URL>

Create the database
^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   python manage.py migrate

Collect the static files
^^^^^^^^^^^^^^^^^^^^^^^^

These commands will compile and collect the static files (CSS, JS, etc).

.. code-block:: shell

   python manage.py compilestatic
   python manage.py collectstatic --noinput

Create an administrator account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will be prompted for a name, email, and password.
This account is needed to access the ``/admin`` page.
You can create multiple administrator accounts.

.. code-block:: shell

   python manage.py createsuperuser

Enable HTTPS
^^^^^^^^^^^^

If you want to enable HTTPS, run this command:

.. code-block:: shell

   python manage.py https on

To disable it, run:

.. code-block:: shell

   python manage.py https off

Finally, set up the server
^^^^^^^^^^^^^^^^^^^^^^^^^^

To set up the server you will need Apache, Nginx or any other web server that supports Django.
Make sure the web server has the necessary permissions to access all the relevant files.
Also, create the ``media`` and ``log`` directories beforehand to avoid possible errors.

Apache example
~~~~~~~~~~~~~~

Apache requires `mod_wsgi <https://modwsgi.rtfd.io/en/latest/>`_ to be installed.

.. literalinclude:: examples/apache.conf
   :language: apache
   :lines: 1-28

Nginx example
~~~~~~~~~~~~~

Nginx requires `uwsgi <https://uwsgi-docs.rtfd.io/en/latest/>`_ to be installed.

.. literalinclude:: examples/nginx.conf
   :language: nginx
   :lines: 1-27

Don't forget to run uwsgi:

.. code-block:: shell

   uwsgi --socket 127.0.0.1:25432 --chdir /var/www/my-site.com/ --module MangAdventure.wsgi

Updating
--------

First, install any new or updated dependencies:

.. code-block:: shell

   pip install -U -r requirements.txt

Then, compile and collect the static files:

.. code-block:: shell

   python manage.py compilestatic
   python manage.py collectstatic --noinput

Finally, update the database:

.. code-block:: shell

   python manage.py migrate

