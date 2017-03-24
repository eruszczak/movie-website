from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.functions import update_ratings


class Command(BaseCommand):
    help = 'Updates ratings of users'

    def handle(self, *args, **options):
        users = User.objects.filter(userprofile__imdb_id__startswith='ur')
        for user in users:
            message = update_ratings(user)
            self.stdout.write(self.style.SUCCESS(message))
