from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    name = 'users'

    def ready(self):
        from . import signals