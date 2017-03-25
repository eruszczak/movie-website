import os
import csv

from django.core.management.base import BaseCommand

from mysite.settings import BACKUP_ROOT
from movie.models import Type, Title
from common.prepareDB_utils import create_m2m_relationships


class Command(BaseCommand):
    help = 'Imports titles from a csv file'

    def handle(self, *args, **options):

        fname = input('Filename?\n')
        if not fname.endswith('.csv'):
            fname += '.csv'
        file_path = os.path.join(BACKUP_ROOT, fname)
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR('Backup does not exist ' + file_path))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            rows = csv.DictReader(f)
            added = 0
            for row in rows:
                if not Title.objects.filter(const=row['const']).exists():
                    print('not exists', row['const'])
                    data = {}
                    added += 1

                    title = Title.objects.create(const=row['const'])
                    actors, directors, genres = row.pop('actor'), row.pop('director'), row.pop('genre')
                    create_m2m_relationships(title, genres=genres, directors=directors, actors=actors)
                    title_type = row.pop('type')

                    data['type'] = Type.objects.get_or_create(name=title_type)[0]
                    for header, value in row.items():
                        data[header] = value or None

                    title, created = Title.objects.update_or_create(const=row['const'], defaults=data)
                    assert not created

        self.stdout.write(self.style.SUCCESS('Restored {} backup from {}'.format(added, file_path)))
