import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from tmdb.api import Tmdb
from titles.models import Title

imdb_id_movie = 'tt0120889'

deleted = Title.objects.filter(imdb_id=imdb_id_movie).delete()
print(deleted)

client = Tmdb().find_by_id(imdb_id_movie)
client.get_title_or_create()
