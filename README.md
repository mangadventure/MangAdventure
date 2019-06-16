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

    Copyright (c) 2018-2019 MangAdventure

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
