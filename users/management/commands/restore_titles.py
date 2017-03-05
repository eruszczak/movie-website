from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from mysite.settings import BACKUP_ROOT
import os
from movie.models import Type, Director, Genre, Actor, Title, Watchlist, Favourite
from recommend.models import Recommendation
from .backup_titles import tables


def clear_titles():
    confirm = input('Do you want to clear the tables?\n')
    if confirm in ('yes', 'y'):
        Watchlist.objects.all().delete()
        Favourite.objects.all().delete()
        Recommendation.objects.all().delete()

        Title.objects.all().delete()
        Type.objects.all().delete()
        Director.objects.all().delete()
        Genre.objects.all().delete()
        Actor.objects.all().delete()


class Command(BaseCommand):
    help = 'Dumps title-related tables into json files'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        clear_titles()

        folder = input('Folder name?\n')
        directory = os.path.join(BACKUP_ROOT, folder)
        if not os.path.exists(directory):
            self.stdout.write(self.style.ERROR('Backup does not exist ' + directory))
            return

        for table in tables:
            filename = os.path.join(directory, table + '.json')
            call_command('loaddata', filename)
        self.stdout.write(self.style.SUCCESS('Restored backup from ' + directory))
