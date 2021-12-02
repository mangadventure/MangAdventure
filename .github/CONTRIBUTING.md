# Contributing to MangAdventure

*Thank you for your interest in contributing!*

## Issues

Security vulnerabilities ought to be reported according to our [security policy][security].

For any other issue, follow these steps:

1. Check whether it's already on our [issue tracker][issues].
2. Make sure you are using our [latest][] release.
3. Search the internet (Google/Stack Overflow/etc.).
4. If still needed, [submit][new-issue] it using the corresponding template.

## Pull Requests

Before submitting a [pull request][pulls], please read the guidelines below.

### Development

You can clone and install the project with the following commands:

```sh
git clone https://github.com/mangadventure/MangAdventure
cd MangAdventure
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,docs,debug]
```

Before proceeding, there are some settings you will need to configure.
<br>To configure them, copy the `.env.example` file to `.env` and edit it.

Now, you can set up the project and run a development server:

```sh
mangadventure migrate # create database
mangadventure collectstatic # collect static files
mangadventure createsuperuser # create administrator
export MANGADV_DEBUG=1 # enable debug mode
mangadventure runserver # start server
```

After starting the server, you can go to [http://localhost:8000/admin-panel/](http://localhost:8000/admin-panel/) and
log in with the administrator account you created earlier to add content to the site.

You can lint the code and run tests like so:

```sh
flake8 && isort -q -c --df . # lint
py.test # run tests
```

### Code Style

Follow the style defined by [EditorConfig](../.editorconfig).

### Commit Messages

* Limit the title to 50 characters.
* Use imperative form in the title.
  * "Fix" rather than "Fixed" or "Fixes".
* Start the title with a capital letter.
* Do not include tags like `(feat):` or `[BUG]`.
  * `[no ci]` is used to skip workflows.
* Use the body to elaborate if needed.
* Wrap lines in the body to 72 characters.

[pulls]: https://github.com/mangadventure/MangAdventure/pulls
[documentation]: https://mangadventure.readthedocs.io/en/latest/
[latest]: https://github.com/mangadventure/MangAdventure/releases/latest
[security]: https://github.com/mangadventure/MangAdventure/security/policy
[issues]: https://github.com/mangadventure/MangAdventure/issues?q=is%3Aissue
[new-issue]: https://github.com/mangadventure/MangAdventure/issues/new/choose
