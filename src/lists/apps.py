from django.apps import AppConfig


class ListsConfig(AppConfig):
    name = 'lists'

    def ready(self):
        from . import signals
