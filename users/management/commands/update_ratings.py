from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from common.prepareDB import update_from_rss
from time import sleep


class Command(BaseCommand):
    help = 'Updates ratings of users'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        results = []
        for user in User.objects.filter(userprofile__imdb_id__isnull=False):
            print(user.username)
            result = update_from_rss(user)
            # if result is not None:
            #     results.append(result)
            #     self.stdout.write(self, '{} updated {}'.format(user.username, result))
            #     sleep(5)
            # else:
            #     self.stdout.write(self.style.ERROR('{} not updated'.format(user.username)))

        self.stdout.write(self.style.SUCCESS(
            'Updated {} titles for {} users'.format(sum(r for r in results), len(results))))
