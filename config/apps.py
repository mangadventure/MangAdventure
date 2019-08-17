from constance.apps import ConstanceConfig


class SiteConfig(ConstanceConfig):
    verbose_name = 'Configuration'
    verbose_name_plural = 'Configuration'

    def ready(self):
        __import__('config.receivers')
        super(SiteConfig, self).ready()
