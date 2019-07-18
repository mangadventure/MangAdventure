from constance.apps import ConstanceConfig


class SiteConfig(ConstanceConfig):
    verbose_name = 'configuration'
    verbose_name_plural = 'configuration'

    def ready(self):
        __import__('config.receivers')
        super(SiteConfig, self).ready()
