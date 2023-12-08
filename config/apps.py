"""App configuration."""

from django.apps import AppConfig
from django.conf import settings

from PIL import Image


class SiteConfig(AppConfig):
    """Configuration for the config app."""
    name = 'config'
    verbose_name = 'Configuration'
    verbose_name_plural = 'Configuration'

    def ready(self):
        """Configure the app when it's ready."""
        super().ready()

        # we don't need to attempt to fetch up to 21 results
        # to figure out if there's an error in the get query
        __import__('django').db.models.query.MAX_GET_RESULTS = 3

        # create manifest icons
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


__all__ = ['SiteConfig']
