from os.path import exists, join

from django.conf import settings
from django.contrib.sites.models import Site
from django.dispatch import receiver

from constance.signals import config_updated
from sass import compile as sassc

SCSS_DEFS = {
    'MAIN_BACKGROUND': '#ffffff',
    'ALTER_BACKGROUND': '#aaaaaa',
    'MAIN_TEXT_COLOR': '#000000',
    'ALTER_TEXT_COLOR': '#555555',
    'SHADOW_COLOR': '#444444',
    'FONT_NAME': 'Lato'
}

SCSS_VARS = """\
$main-bg: %(MAIN_BACKGROUND)s;
$alter-bg: %(ALTER_BACKGROUND)s;
$main-fg: %(MAIN_TEXT_COLOR)s;
$alter-fg: %(ALTER_TEXT_COLOR)s;
$shadow-color: %(SHADOW_COLOR)s;
$font-family: %(FONT_NAME)s;
"""

_variables = join(settings.STATIC_ROOT, 'styles', '_variables.scss')


def _generate_variables(func):
    with open(_variables, 'w') as s:
        s.write(SCSS_VARS % {k: func(k) for k in SCSS_DEFS})
    if not settings.DEBUG:
        sassc(
            dirname=(
                join(settings.STATIC_ROOT, 'styles'),
                join(settings.STATIC_ROOT, 'COMPILED', 'styles')
            ),
            output_style='compressed',
            precision=7
        )


@receiver(config_updated)
def constance_updated(sender, key, old_value, new_value, **kwargs):
    if key == 'NAME':
        site = Site.objects.get_or_create(pk=1)[0]
        site.domain = site.domain or settings.SITE_DOMAIN or 'example.com'
        site.name = new_value
        site.save()
    elif key in SCSS_DEFS:
        _generate_variables(sender.__getattr__)


if not exists(_variables):
    _generate_variables(SCSS_DEFS.__getitem__)


__all__ = ['constance_updated']
