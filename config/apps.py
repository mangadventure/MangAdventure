from django.apps import AppConfig
from django.db import connection

SCSS_VARS = """\
$main-bg: %(MAIN_BG_COLOR)s;
$alter-bg: %(ALTER_BG_COLOR)s;
$main-fg: %(MAIN_TEXT_COLOR)s;
$alter-fg: %(ALTER_TEXT_COLOR)s;
$shadow-color: %(SHADOW_COLOR)s;
$font-family: %(FONT_NAME)s;
"""


class SiteConfig(AppConfig):
    name = 'config'
    verbose_name = 'Configuration'
    verbose_name_plural = 'Configuration'

    def ready(self):
        super(SiteConfig, self).ready()

        if 'django_site' in connection.introspection.table_names():
            self._configure()

    def _configure(self):
        from django.conf import settings
        from django.contrib.sites.models import Site

        site = Site.objects.get_or_create(pk=settings.SITE_ID)[0]
        site.domain = settings.CONFIG['DOMAIN']
        site.name = settings.CONFIG['NAME']
        site.save()

        self._compile_scss(settings)

    def _compile_scss(self, settings):
        from sass import compile as sassc

        src = settings.STATIC_ROOT / 'styles'
        dst = settings.STATIC_ROOT / 'COMPILED' / 'styles'

        with open(src / '_variables.scss', 'w') as f:
            f.write(SCSS_VARS % settings.CONFIG)

        sassc(dirname=(src, dst), output_style='compressed')

        src = settings.STATIC_ROOT / 'extra'
        dst = settings.STATIC_ROOT / 'COMPILED' / 'extra'

        sassc(dirname=(src, dst), output_style='compressed')
