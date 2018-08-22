# MangAdventure [![release](https://img.shields.io/github/release/evangelos-ch/MangAdventure/all.svg)](https://github.com/evangelos-ch/MangAdventure/releases)

MangAdventure, aka MangADV, is a simple manga hosting webapp.

It is fully written in Django, SCSS and Vanilla JS. No PHP, no Bootstrap, no jQuery.

## Table of Contents

- [Features](#features)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [Changelog](#changelog)
- [Credits](#credits)

## Features

- Open source.
- Simple and configurable.
- Upload chapters as zip files.
- More features coming.

## Dependencies

- [Python 3](https://www.python.org/downloads/)
- [Django](https://www.djangoproject.com/download/)
- [Django Next-Prev](https://pypi.org/project/django-next-prev/)
- [Django Constance](https://django-constance.readthedocs.io/en/latest/#installation)
- [Django Picklefield](https://pypi.org/project/django-picklefield/)
- [Django Static Precompiler](https://django-static-precompiler.readthedocs.io/en/stable/installation.html)
- [LibSass](https://sass.github.io/libsass-python/#install)
- [Pillow](https://pillow.readthedocs.io/en/latest/installation.html#basic-installation)

## Installation

**WARNING: This project is still in an experimental state and may be unstable. Proceed at your own risk.**

First, install the dependencies. If you already have Python & [pip](https://pip.pypa.io/en/stable/installing/), you can install all the required Python modules with:

```shell
pip install -r requirements.txt
```

Then, download and unzip the [latest release](https://github.com/evangelos-ch/MangAdventure/releases/latest) and follow these steps to initialize the site:

### Generate a secret key:

```shell
python manage.py generatekey
```

### Configure the site URL:

Replace `<URL>` with the URL of your website.

```shell
python manage.py configureurl <URL>
```

### Create the database:

```shell
python manage.py migrate
```

### Collect the static files:

These commands will compile and collect the static files (CSS, JS, etc).

```shell
python manage.py compilestatic
python manage.py collectstatic --noinput
```

### Create an administrator account:

You will be prompted for a name, email, and password.

```shell
python manage.py createsuperuser
```

### Enable HTTPS:

If you want to enable HTTPS, run this command:

```shell
python manage.py https on
```

To disable it, run:

```shell
python manage.py https off
```

### Finally, set up the server:

To set up the server you will need Apache, Nginx or any other web server that supports Django.

*Make sure the web server has the necessary permissions to access all the relevant files.*

*Also, create the `media` and `log` directories beforehand to avoid possible errors.*

#### Apache example

Apache requires mod_wsgi to be installed.

```apache
<VirtualHost *:80>
    ServerName my-site.com
    ServerAlias www.my-site.com
    ServerAdmin you@email.com

    <Location /admin>
        LimitRequestBody 51000000
    </Location>

    Alias /static /var/www/my-site.com/static
    <Directory /var/www/my-site.com/static>
        Require all granted
    </Directory>

    Alias /media  /var/www/my-site.com/media
    <Directory /var/www/my-site.com/media>
        Require all granted
    </Directory>

    WSGIDaemonProcess my-site python-path=/var/www/my-site.com:/var/www/my-site.com/.venv/lib/python3.6/site-packages
    WSGIProcessGroup my-site
    WSGIScriptAlias / /var/www/my-site.com/MangAdventure/wsgi.py process-group=my-site
    <Directory /var/www/my-site.com/MangAdventure>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
</VirtualHost>
```

#### Nginx example

Nginx requires uwsgi to be installed.

```nginx
server {
    listen 80;
    server_name my-site.com www.my-site.com;
    charset utf-8;

    location /admin {
        client_max_body_size 51M;
    }

    location /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static {
        alias /var/www/my-site.com/static;
    }

    location /media  {
        alias /var/www/my-site.com/media;
    }

    location / {
        uwsgi_pass 127.0.0.1:25432;
        include uwsgi_params;
    }
}
```

Don't forget to run uwsgi:

```shell
/var/www/my-site.com/.venv/bin/uwsgi --socket 127.0.0.1:25432 --chdir /var/www/my-site.com/ --module MangAdventure.wsgi
```

## Configuration

You can configure the site via the admin panel. If you want to overwrite the styling of the site, you can write some SCSS (or regular CSS) in the `static/extra/styles.scss` file.

## Development

To debug the server set the environment variable `MANGADV_DEBUG` to `true`. **Don't do this in production.**

You shouldn't use the production server during development. You can use Django's `runserver` command to run a development server on `127.0.0.1:8000` (or any other address you specify).

## Changelog

You can view the changelog [here](CHANGELOG.md).

There's also a [roadmap](ROADMAP.md) for future releases.

## Credits

- Inspired by [FoOlSlide 2](https://github.com/chocolatkey/FoOlSlide2)
- Icons by [Fork Awesome](https://forkawesome.github.io/Fork-Awesome/)

