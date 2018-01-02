import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from django.contrib.auth import get_user_model

from importer.utils import import_ratings_from_csv
from titles.models import Title
from tmdb.api import TmdbWrapper

User = get_user_model()


def test_csv():
    user = User.objects.all().first()
    import_ratings_from_csv(user, 'G:/code/PycharmProjects/movie website/media/test.csv')

    # update_user_ratings_csv(user, 'G:/code/PycharmProjects/movie website/media/accounts/imdb.csv')

# test_csv()

# check add new tite
# update that title
# check popular
# check import/eexport


# for t in Title.objects.filter(tmdb_id='1414'):
#     # print(t.similar.clear())
# #     print(t, t.imdb_id)
#     tmdb_instance = t.get_tmdb_instance()
#     tmdb_instance(title=t).update()

# Title.objects.filter(tmdb_id='1414').delete()
# for imdb_id in ['tt0286486', 'tt0133363']:
#     TmdbWrapper().get(imdb_id=imdb_id)

imdb_id_movie = 'tt0120889'
# tmdb_id_movie = '12159'

# imdb_id_series = 'tt4574334'
tmdb_id_series = '66732'


# deleted = Title.objects.filter(imdb_id=collection_id).delete()
# Collection.objects.all().delete()
# deleted = Title.objects.filter(imdb_id=imdb_id_movie).delete()
# deleted = Title.objects.filter(tmdb_id=tmdb_id_series).delete()
# print(deleted)

# title = TmdbWrapper().get(imdb_id_movie)
# title = client.get_title_or_create()
# print(title.collection.all())

# t = Title.objects.get(tmdb_id=tmdb_id_series)
# print(t.cast.all())
# print(t.crew.all())

# for x in t.casttitle_set.all():
#     print(x)

# for x in t.castcrew_set.all():
#     print(x)

# popular_movies = PopularMovies().get()
# print(popular_movies)

# for title in Title.objects.all():
#     print(title.name)
#     imdb_id = title.imdb_id
#     print(title.delete())
#     TmdbWrapper().get(imdb_id)

