from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        __import__('users.receivers')
        super(UsersConfig, self).ready()
