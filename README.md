# MangAdventure

[![Release](https://img.shields.io/github/release/mangadventure/MangAdventure.svg?include_prereleases&label=Release&logo=github)](https://github.com/mangadventure/MangAdventure/releases)
[![Tests](https://github.com/mangadventure/MangAdventure/workflows/Tests/badge.svg)](https://github.com/mangadventure/MangAdventure/actions?query=workflow%3ATests)
[![Coverage](https://img.shields.io/coveralls/github/mangadventure/MangAdventure?label=Coverage&logo=coveralls)](https://coveralls.io/github/mangadventure/MangAdventure)
[![Discord](https://img.shields.io/discord/678589874475106312?color=7289DA&label=Discord&logo=discord)](https://discord.gg/GsJyhSz)

MangAdventure, aka MangADV, is a simple manga hosting CMS.

It is written in Django, SCSS and Vanilla JS. No PHP, no Node.js, no jQuery.

## Features

* [x] Is open source.
* [x] Is fully configurable.
* [x] Includes JSON API.
* [x] Includes RSS & Atom feeds.
* [x] Doesn't require JavaScript.
* [x] Supports searching for series.
* [x] Supports users.
  * [x] OAuth registration.
  * [x] Series bookmarks.
  * [x] Chapter downloads.
  * [ ] Comments.
* [x] Supports scheduled releases.
* [x] Supports custom chapter names.
* [x] Allows for migration from FoolSlide2.
* [ ] More features coming soon...

## Documentation

The documentation is available on [Read the Docs][rtfd].

[rtfd]: https://mangadventure.rtfd.io

## Sites

You can find a list of sites that use MangAdventure in the [wiki][wiki].

If you use MangAdventure for your own site, please add it there.

[wiki]: https://github.com/mangadventure/MangAdventure/wiki

## Development

<!-- We'll write proper guidelines soon. -->

To debug the app set the environment variable `MANGADV_DEBUG`
to `true`. **Don't do this in production.**

You can use Django's `runserver` command to run a development
server on `127.0.0.1:8000` (or any other address you specify).
You shouldn't use the development server during production.

## Credits

* Inspired by [FoOlSlide 2](https://github.com/chocolatkey/FoOlSlide2)
* Search results are sorted using [tablesort](https://tristen.ca/tablesort/demo/)
* Info pages & comments use the [TinyMCE editor](https://www.tiny.cloud/docs-4x/)
* Browser logos are taken from [alrra/browser-logos](https://github.com/alrra/browser-logos)

## License

    Copyright (c) 2018-2021 MangAdventure

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
