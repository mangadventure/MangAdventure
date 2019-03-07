from constance.apps import ConstanceConfig


class SiteConfig(ConstanceConfig):
    verbose_name = 'Site Configuration'
    verbose_name_plural = 'Site Configuration'

    def ready(self):
        __import__('config.receivers')
        super(SiteConfig, self).ready()

