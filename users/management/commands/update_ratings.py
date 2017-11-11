from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from users.functions import update_ratings

User = get_user_model()


class Command(BaseCommand):
    help = 'Updates ratings of users'

    def handle(self, *args, **options):
        users = User.objects.filter(imdb_id__startswith='ur')
        for user in users:
            update_ratings(user)
