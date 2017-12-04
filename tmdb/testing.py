import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from tmdb.api import Tmdb
from titles.models import Title, Person

# imdb_id_movie = 'tt0120889'
# tmdb_id_movie = '12159'

# imdb_id_series = 'tt4574334'
tmdb_id_series = '66732'

# deleted = Title.objects.filter(imdb_id=tmdb_id_movie).delete()
deleted = Title.objects.filter(tmdb_id=tmdb_id_series).delete()
# # print(deleted)
#
client = Tmdb().find_by_id(tmdb_id_series)
title = client.get_title_or_create()


t = Title.objects.get(tmdb_id=tmdb_id_series)
print(t.cast.all())
print(t.crew.all())

for x in t.casttitle_set.all():
    print(x)

# for x in t.castcrew_set.all():
#     print(x)