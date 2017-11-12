from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.functions import update_watchlist

User = get_user_model()


class Command(BaseCommand):
    help = 'Updates watchlist of accounts'

    def handle(self, *args, **options):
        for user in User.objects.filter(imdb_id__startswith='ur'):
            update_watchlist(user)
