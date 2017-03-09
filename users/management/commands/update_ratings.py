from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from common.prepareDB import update_from_rss, update_from_csv
from time import sleep


class Command(BaseCommand):
    help = 'Updates ratings of users'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        general_count = 0
        users = User.objects.filter(userprofile__imdb_id__startswith='ur')
        for user in users:
            # if user.username == 'test':
            #     updated_titles, count = update_from_csv(user)
            #     self.stdout.write(self.style.SUCCESS('{} updated {} {}'.format(user.username, count, updated_titles)))
            # continue
            data = update_from_rss(user)
            if data is not None:
                titles, count = data
                if titles:
                    general_count += count
                    self.stdout.write(self.style.SUCCESS('{} updated {}'.format(user.username, count)))
                    sleep(5)
                else:
                    self.stdout.write(self.style.SUCCESS('nothing new'))
            else:
                self.stdout.write(self.style.ERROR('{} not updated'.format(user.username)))

        self.stdout.write(
            self.style.SUCCESS(
                'Updated {} titles for {} users'.format(general_count, users.count())
            )
        )
