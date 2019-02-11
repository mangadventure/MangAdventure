from django.conf import settings
from django.dispatch import receiver
from constance.signals import config_updated
from sass import compile as sassc
from os.path import join


KEYS = [
    'MAIN_BACKGROUND',
    'ALTER_BACKGROUND',
    'MAIN_TEXT_COLOR',
    'ALTER_TEXT_COLOR',
    'SHADOW_COLOR',
    'FONT_NAME'
]

VARIABLES = """\
$main-bg: %(MAIN_BACKGROUND)s;
$alter-bg: %(ALTER_BACKGROUND)s;
$main-fg: %(MAIN_TEXT_COLOR)s;
$alter-fg: %(ALTER_TEXT_COLOR)s;
$shadow-color: %(SHADOW_COLOR)s;
$font-family: %(FONT_NAME)s;
"""


@receiver(config_updated)
def constance_updated(sender, key, old_value, new_value, **kwargs):
    if key in KEYS:
        scss = join(settings.STATIC_ROOT, 'styles', '_variables.scss')
        with open(scss, 'w') as s:
            s.write(VARIABLES % dict(
                (k, sender.__getattr__(k)) for k in KEYS
            ))
        if not settings.DEBUG:
            sassc(
                dirname=(
                    join(settings.STATIC_ROOT, 'styles'),
                    join(settings.STATIC_ROOT, 'COMPILED', 'styles')
                ),
                output_style='compressed',
                precision=7
            )


__all__ = ['constance_updated']

