from unittest import TestCase

from titles.constants import MOVIE, SERIES
from titles.models import Title
from tmdb.api import get_tmdb_concrete_class, MovieTmdb, SeriesTmdb, TmdbWrapper


class APITests(TestCase):
    imdb_id_movie = 'tt0120889'
    imdb_id_series = 'tt4574334'
    tmdb_id_movie = '12159'
    tmdb_id_series = '66732'
    collection_id = 'tt0120737'

    def setUp(self):
        self.movie = TmdbWrapper().get(self.imdb_id_movie)

    def test_get_tmdb_concrete_class(self):
        self.assertIs(MovieTmdb, get_tmdb_concrete_class(MOVIE))
        self.assertIs(SeriesTmdb, get_tmdb_concrete_class(SERIES))

    def test_title_returned(self):
        self.assertIsInstance(self.movie, Title)

    def test_movie_returned(self):
        self.assertEqual(self.movie.type, MOVIE)

    def test_invalid_id_title_not_returned(self):
        pass

    def test_second_request_is_from_cache(self):
        pass
