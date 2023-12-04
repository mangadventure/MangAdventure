#!/bin/bash -e

# NOTE: this script is meant for render.com deployments

printf 'Setting up environment variables.\n'
# shellcheck disable=SC2016
sed .env.example > .env \
  -e '/ADMIN=/d' \
  -e 's/none/weserv/' \
  -e 's/favicon.ico/logo.png/' \
  -e 's/EMAIL_URL=".*"/EMAIL_URL="console:"/' \
  -e 's/${DOMAIN},www.${DOMAIN}/.onrender.com/' \
  -e 's/<user>@${DOMAIN}/${DJANGO_SUPERUSER_EMAIL}/'

printf 'Creating the extra style file.\n'
mkdir -p static/extra && touch static/extra/style.scss

printf 'Installing the dependencies.\n'
pip install -q -e '.[redis,uwsgi]'

printf 'Downloading the website logo.\n'
./manage.py shell -c $'
from django.conf import settings
from os import getenv as env
from requests import get
settings.MEDIA_ROOT.mkdir(exist_ok=True)
(settings.MEDIA_ROOT / "logo.png").write_bytes(
    get(env("LOGO_URL"), allow_redirects=True).content
)
(settings.STATIC_ROOT / "COMPILED").mkdir(exist_ok=True)
'

printf 'Setting up the database.\n'
./manage.py migrate -v0 --no-input

printf 'Collecting static files.\n'
./manage.py collectstatic -v0 --no-input

printf 'Loading the categories fixture.\n'
./manage.py loaddata -v0 categories

printf 'Creating the Django superuser.\n'
./manage.py createsuperuser -v0 --no-input
