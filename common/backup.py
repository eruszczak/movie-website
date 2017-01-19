import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.core.management import call_command
from movie.models import Type, Director, Genre, Actor, Title, Watchlist, Favourite
from recommend.models import Recommendation

tables = ['movie.type', 'movie.director', 'movie.genre', 'movie.actor', 'movie.title']


def backup_titles():
    for table in tables:
        filename = 'backup/{}.json'.format(table)
        with open(filename, 'w') as f:
            call_command('dumpdata', table, stdout=f)


def clear_titles():
    confirm = input('Do you want to clear the tables?')
    if confirm in ('yes', 'y'):
        Watchlist.objects.all().delete()
        Favourite.objects.all().delete()
        Recommendation.objects.all().delele()

        Title.objects.all().delete()
        Type.objects.all().delete()
        Director.objects.all().delete()
        Genre.objects.all().delete()
        Actor.objects.all().delete()


def restore_titles():
    # call_command('makemigrations', 'movie')
    # call_command('migrate', 'movie')
    for table in tables:
        filename = 'backup/{}.json'.format(table)
        call_command('loaddata', filename)


# backup_titles()
# restore_titles()
