"""App configuration."""

from django.apps import AppConfig
from django.conf import settings
from django.db import connection

#: Variables used to generate ``static/styles/_variables.scss``.
SCSS_VARS = """\
$main-bg: %(MAIN_BG_COLOR)s;
$alter-bg: %(ALTER_BG_COLOR)s;
$main-fg: %(MAIN_TEXT_COLOR)s;
$alter-fg: %(ALTER_TEXT_COLOR)s;
$shadow-color: %(SHADOW_COLOR)s;
$font-family: %(FONT_NAME)s;
"""


class SiteConfig(AppConfig):
    """Configuration for the config app."""
    name = 'config'
    verbose_name = 'Configuration'
    verbose_name_plural = 'Configuration'

    def ready(self):
        """Configure the site when the app is ready."""
        super().ready()

        if 'django_site' in connection.introspection.table_names():
            self._init_site()
            self._create_icons()
            self._compile_scss()

        # we don't need to attempt to fetch up to 21 results
        # to figure out if there's an error in the get query
        __import__('django').db.models.query.MAX_GET_RESULTS = 3

    @staticmethod
    def _init_site():
        from django.contrib.sites.models import Site

        site = Site.objects.get_or_create(pk=settings.SITE_ID)[0]
        site.domain = settings.CONFIG['DOMAIN']
        site.name = settings.CONFIG['NAME']
        site.save()

    @staticmethod
    def _compile_scss():
        from sass import compile as sassc

        src = settings.STATIC_ROOT / 'styles'
        dst = settings.STATIC_ROOT / 'COMPILED' / 'styles'
        (src / '_variables.scss').write_text(SCSS_VARS % settings.CONFIG)
        sassc(dirname=(src, dst), output_style='compressed')

        src = settings.STATIC_ROOT / 'extra'
        dst = settings.STATIC_ROOT / 'COMPILED' / 'extra'
        sassc(dirname=(src, dst), output_style='compressed')

    @staticmethod
    def _create_icons():
        from PIL import Image

        logo = settings.BASE_DIR / settings.CONFIG['LOGO_OG'].lstrip('/')
        if logo.is_file():
            icon192 = settings.MEDIA_ROOT / 'icon-192x192.webp'
            if not icon192.exists():
                img = Image.open(logo)
                img.thumbnail((192, 192), Image.LANCZOS)
                img.save(icon192, 'WEBP', lossless=True)
                img.close()

            icon512 = settings.MEDIA_ROOT / 'icon-512x512.webp'
            if not icon512.exists():
                img = Image.open(logo)
                img.thumbnail((512, 512), Image.LANCZOS)
                img.save(icon512, 'WEBP', lossless=True)
                img.close()


__all__ = ['SCSS_VARS', 'SiteConfig']
