from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from mysite.settings import BACKUP_ROOT
import os
from datetime import datetime
from django.contrib.auth.models import User
from movie.models import Rating
import csv


class Command(BaseCommand):
    help = 'Dumps user ratings into csv file'

    def handle(self, *args, **options):
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # u = args[0] if len(args) == 1 else None
        users = User.objects.all()
        # print(u)
        # if u is not None:
        #     try:
        #         users = [User.objects.get(username=u)]
        #     except User.DoesNotExist:
        #         raise CommandError('User "%s" does not exist' % u)
        for a in args:
            print(a)

        for user in users:
            directory = os.path.join(BACKUP_ROOT, user.username)
            if not os.path.exists(directory):
                os.makedirs(directory)
            user_ratings = Rating.objects.filter(user=user).select_related('title')
            filename = os.path.join(directory, '{}ratings{}.csv'.format(user_ratings.count(), now))
            with open(filename, 'w') as f:
                headers = ['const', 'rate_date', 'rate']
                writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\n')
                writer.writeheader()
                for r in user_ratings:
                    writer.writerow({
                        'const': r.title.const,
                        'rate_date': r.rate_date,
                        'rate': r.rate
                    })
            self.stdout.write(self.style.SUCCESS('Created csv in ' + filename))

