from django.apps import AppConfig


class TitlesConfig(AppConfig):
    name = 'titles'

    def ready(self):
        from . import signals
