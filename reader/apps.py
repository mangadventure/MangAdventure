from django.apps import AppConfig


class ReaderConfig(AppConfig):
    name = 'reader'

    def ready(self):
        __import__('reader.receivers')
        super(ReaderConfig, self).ready()

