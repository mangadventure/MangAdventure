# MangAdventure [![release](https://img.shields.io/github/release/mangadventure/MangAdventure/all.svg)](https://github.com/mangadventure/MangAdventure/releases)

MangAdventure, aka MangADV, is a simple manga hosting CMS.

It is written in Django, SCSS and Vanilla JS. No PHP, no Node.js, no jQuery.

## Features

* [x] Is open source.
* [x] Is fully configurable.
* [x] Includes JSON API.
* [x] Works even without JavaScript.
* [x] Supports searching for series.
* [x] Supports users. <!--(comments & bookmarks too) soon-->
* [x] Allows for migration from FoolSlide2.
* [ ] More features coming soon...

## Documentation

The documentation is available on [Read the Docs](https://mangadventure.rtfd.io).

## Configuration

You can configure the site via the admin panel.

To override the styling of the site, you can write some
SCSS (or regular CSS) in the `static/extra/styles.scss` file.

## Development

To debug the app set the environment variable `MANGADV_DEBUG`
to `true`. **Don't do this in production.**

You can use Django's `runserver` command to run a development
server on `127.0.0.1:8000` (or any other address you specify).
You shouldn't use the development server during production.

## Credits

* Inspired by [FoOlSlide 2](https://github.com/chocolatkey/FoOlSlide2)
* Search results are sorted using [tristen/tablesort](https://github.com/tristen/tablesort)
* Info pages use the [TinyMCE editor](https://www.tiny.cloud/)
* Browser logos from [alrra/browser-logos](https://github.com/alrra/browser-logos)

## License

[MIT](LICENSE)


