from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from common.prepareDB import get_watchlist
from time import sleep


class Command(BaseCommand):
    help = 'Updates watchlist of users'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        results = []
        for user in User.objects.filter(userprofile__imdb_id__isnull=False):
            result = get_watchlist(user)
            if result is not None:
                results.append(result)
                self.stdout.write(self, '{} new {}; deleted {}'.format(user.username, result[0], result[1]))
                sleep(5)
            else:
                self.stdout.write(self.style.ERROR('{} not updated'.format(user.username)))

        self.stdout.write(self.style.SUCCESS(
            'New {}; deleted {} titles for {} users'.format(
                sum(r[0] for r in results), sum(r[1] for r in results), len(results))))
