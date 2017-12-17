from django.core.management.base import BaseCommand

from titles.tmdb_api import TmdbTaskRunner


class Command(BaseCommand):

    def handle(self, *args, **options):
        TmdbTaskRunner().run()
