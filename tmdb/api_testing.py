import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from django.contrib.auth import get_user_model

from importer.utils import import_ratings_from_csv

User = get_user_model()


def test_csv():
    user = User.objects.all().first()
    import_ratings_from_csv(user, 'G:/code/PycharmProjects/movie website/media/test.csv')

    # update_user_ratings_csv(user, 'G:/code/PycharmProjects/movie website/media/accounts/imdb.csv')

test_csv()


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

