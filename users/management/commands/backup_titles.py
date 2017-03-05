from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from mysite.settings import BACKUP_ROOT
import os
from datetime import datetime


tables = ['movie.type', 'movie.director', 'movie.genre', 'movie.actor', 'movie.title']


class Command(BaseCommand):
    help = 'Dumps title-related tables into json files'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        directory = os.path.join(BACKUP_ROOT, now)
        if not os.path.exists(directory):
            os.makedirs(directory)

        for table in tables:
            filename = os.path.join(directory, table + '.json')
            with open(filename, 'w') as f:
                call_command('dumpdata', table, stdout=f)
        self.stdout.write(self.style.SUCCESS('Created backup in ' + BACKUP_ROOT))
