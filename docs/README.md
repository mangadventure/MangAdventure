# MangAdventure

MangAdventure, aka MangADV, is a simple manga hosting webapp. It is fully written in Django, SCSS and Vanilla JS. No PHP, no Bootstrap, no jQuery.

## Table of Contents

- [Features](#features)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [Roadmap](#roadmap)
- [Credits](#credits)

## Features

- Open source.
- Simple and configurable.
- Upload chapters as zip files.
- More features coming.

## Dependencies

- [Python 3](https://www.python.org/downloads/)
- [Django](https://www.djangoproject.com/download/)
- [DJ-Static](https://pypi.org/project/dj-static/)
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
python manage.py migrate --run-syncdb
```

### Collect the static files:

This will collect static files used by the admin panel (CSS, JS, etc). Type `yes` when prompted.

```shell
python manage.py collectstatic
```

### Create an administrator account:

You will be prompted for a name, email, and password.

```shell
python manage.py createsuperuser
```

### Finally, run the server:

```shell
python manage.py runserver
```

## Configuration

You can configure the site's config via the admin panel.

If you want to overwrite the styling of the site, you can write some SCSS (or regular CSS) in the `static/extra/styles.scss` file.

## Development

To debug the server set the environment variable `MANGADV_DEBUG` to `true`. **Don't do this in production.**

## Roadmap

You can view the roadmap [here](ROADMAP.md)

## Credits

- Inspired by [FoOlSlide 2](https://github.com/chocolatkey/FoOlSlide2)
- Icons by [Fork Awesome](https://forkawesome.github.io/Fork-Awesome/)

