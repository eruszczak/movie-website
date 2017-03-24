import os
import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from mysite.settings import BACKUP_ROOT
from movie.models import Title


class Command(BaseCommand):
    help = 'Dumps title data into a csv file'

    def handle(self, *args, **options):
        now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        titles = Title.objects.all()
        fname = os.path.join(BACKUP_ROOT, '{}titles{}{}'.format(titles.count(), now, '.csv'))
        headers = Title._meta.get_fields(include_parents=False)
        excluded_headers = ('rating', 'id', 'watchlist', 'favourite', 'recommendation')
        headers = [h.name for h in headers if h.name not in excluded_headers]

        with open(fname, 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\n')
            writer.writeheader()
            for title in titles:
                data = {}
                for header in headers:
                    val = False
                    if val in ['actor', 'director', 'genre']:
                        instances = title.actor.all() if header == 'actor'\
                            else title.director.all() if header == 'director'\
                            else title.genre.all()
                        val = ', '.join(obj.name for obj in instances)
                    val = val or getattr(title, header)
                    data[header] = val
                    # todo how to handle empty vals
                writer.writerow(data)
        self.stdout.write(self.style.SUCCESS('Created: ' + fname))
