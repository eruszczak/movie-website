import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.core.management import call_command

tables = ['movie.type', 'movie.director', 'movie.genre', 'movie.actor', 'movie.title']


def backup_titles():
    for table in tables:
        filename = table + '.json'
        with open(filename, 'w') as f:
            call_command('dumpdata', table, stdout=f)


def clear_titles():
    from movie.models import Type, Director, Genre, Actor, Title
    confirm = input('Do you want to delete tables?')
    if confirm in ('yes', 'y'):
        Title.objects.all().delete()
        Type.objects.all().delete()
        Director.objects.all().delete()
        Genre.objects.all().delete()
        Actor.objects.all().delete()


def restore_titles():
    for table in tables:
        filename = table + '.json'
        call_command('loaddata', filename)
        # with open(filename, 'r') as f:
        #     call_command('loaddata', table, stdin=f)
