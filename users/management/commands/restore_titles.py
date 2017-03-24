import os

from django.core.management.base import BaseCommand
from django.core.management import call_command

from mysite.settings import BACKUP_ROOT
from movie.models import Type, Director, Genre, Actor, Title, Watchlist, Favourite
from recommend.models import Recommendation
import csv
from common.prepareDB_utils import create_m2m_relationships
# def clear_titles():
#     confirm = input('Do you want to clear the tables? User data will be lost\n')
#     if confirm in ('yes', 'y'):
#         if input('sure???') in ('yes', 'y'):
#             Watchlist.objects.all().delete()
#             Favourite.objects.all().delete()
#             Recommendation.objects.all().delete()
#
#             Title.objects.all().delete()
#             Type.objects.all().delete()
#             Director.objects.all().delete()
#             Genre.objects.all().delete()
#             Actor.objects.all().delete()


class Command(BaseCommand):
    help = 'Imports titles from a csv file'

    def handle(self, *args, **options):
        # clear_titles()

        # fname = input('Filename?\n')
        fname = '2004titles2017-03-24-12-21-35.csv'
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
                    # create_m2m_relationships(title, genres=genres, directors=directors, actors=actors)

                    title_type = row.pop('type')
                    data['type'] = Type.objects.get_or_create(name=title_type)[0]
                    for header, value in row.items():
                        data[header] = value

                    print(data)
                    print()
                    print(**data)
                    # title, created = Title.objects.update_or_create(const=title['const'], defaults=**data)
                    # assert not created
                    # Title.objects.create(**data)

                    # count = Title.objects.filter(const=title['const']).update(**data)
                    # print(count)
                    # assert count in (0, 1)
                else:
                    print('exists')

        self.stdout.write(self.style.SUCCESS('Restored {} backup from {}'.format(added, file_path)))
