from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.functions import update_watchlist


class Command(BaseCommand):
    help = 'Updates watchlist of users'

    def handle(self, *args, **options):
        for user in User.objects.filter(userprofile__imdb_id__startswith='ur'):
            update_watchlist(user)
