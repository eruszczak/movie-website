from django.core.management.base import BaseCommand
from mysite.settings import BACKUP_ROOT
import os
from datetime import datetime
from django.contrib.auth.models import User
from movie.models import Rating
import csv
from users.functions import create_csv_with_user_ratings


class Command(BaseCommand):
    help = 'Dumps user ratings into csv file'

    def handle(self, *args, **options):
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        for user in User.objects.all():
            directory = os.path.join(BACKUP_ROOT, user.username)
            if not os.path.exists(directory):
                os.makedirs(directory)

            user_ratings = Rating.objects.filter(user=user).select_related('title')
            filename = os.path.join(directory, '{}ratings{}.csv'.format(user_ratings.count(), now))
            with open(filename, 'w') as f:
                headers = ['const', 'rate_date', 'rate']
                writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\n')
                writer.writeheader()
                create_csv_with_user_ratings(writer, user_ratings)
            self.stdout.write(self.style.SUCCESS('Created csv in ' + filename))
