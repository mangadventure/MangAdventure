from constance.apps import ConstanceConfig


class SettingsConfig(ConstanceConfig):
    verbose_name = 'Settings'
    verbose_name_plural = 'Settings'

    def ready(self):
        __import__('config.receivers')

