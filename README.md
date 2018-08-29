# MangAdventure [![release](https://img.shields.io/github/release/evangelos-ch/MangAdventure/all.svg)](https://github.com/evangelos-ch/MangAdventure/releases/latest)

MangAdventure, aka MangADV, is a simple manga hosting webapp.

It is fully written in Django, SCSS and Vanilla JS. No PHP, no Bootstrap, no jQuery.

## Features

* Open source.
* Simple and configurable.
* Upload chapters as zip files.
* Search for series.
* More features coming.

## Documentation

The documentation is available on [Read the Docs](https://mangadventure.rtfd.io).

## Configuration

You can configure the site via the admin panel. If you want to overwrite the styling of the site, you can write some SCSS (or regular CSS) in the `static/extra/styles.scss` file.

## Development

To debug the server set the environment variable ``MANGADV_DEBUG`` to ``true``. **Don't do this in production.**

You shouldn't use the production server during development. You can use Django's ``runserver`` command to run a development server on `127.0.0.1:8000` (or any other address you specify).

## Credits

* Inspired by [FoOlSlide 2](https://github.com/chocolatkey/FoOlSlide2)
* Icons by [Font Awesome 5.2](https://fontawesome.com>)

## License

[MIT](LICENSE)

