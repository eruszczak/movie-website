from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from common.prepareDB import get_watchlist
from time import sleep


class Command(BaseCommand):
    help = 'Updates watchlist of users'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for user in User.objects.filter(userprofile__imdb_id__startswith='ur'):
            data = get_watchlist(user)
            if data is not None:
                updated, updated_count = data['updated']
                deleted, deleted_count = data['deleted']
                self.stdout.write(self.style.SUCCESS('{} new {}; deleted {}'.format(user.username, updated_count, deleted_count)))
                sleep(5)
            else:
                self.stdout.write(self.style.ERROR('{} not updated'.format(user.username)))

        self.stdout.write(self.style.SUCCESS('Finished'))
