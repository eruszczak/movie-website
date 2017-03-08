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
            if user.username == 'test':
                updated_titles, count = update_from_csv(user)
                self.stdout.write(self.style.SUCCESS('{} updated {} {}'.format(user.username, count, updated_titles)))
            continue
            titles, count = update_from_rss(user)
            if titles:
                general_count += count
                self.stdout.write(self.style.SUCCESS('{} updated {}'.format(user.username, count)))
                sleep(5)
                # todo
                # should set some attribute for that user
                # and then while filtering, only get those users that weren't updated for a while
                # i'm doing something similar to this in user views already
            else:
                self.stdout.write(self.style.ERROR('{} not updated'.format(user.username)))

        self.stdout.write(
            self.style.SUCCESS(
                'Updated {} titles for {} users'.format(general_count, users.count())
            )
        )
