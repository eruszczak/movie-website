from titles.constants import MOVIE, SERIES
from tmdb.api import MovieTmdb, SeriesTmdb


def get_tmdb_wrapper_class(title_type):
    """depending on title_type, returns MovieTmdb or SeriesTmdb class"""
    if title_type == MOVIE:
        return MovieTmdb.__class__
    elif title_type == SERIES:
        return SeriesTmdb.__class__
    return None
