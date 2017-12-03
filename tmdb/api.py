import os

import django

from tmdb.base.base import TmdbResponseMixin, BaseTmdb
from tmdb.helpers import get_tmdb_wrapper_class

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

import json

from titles.constants import MOVIE, SERIES
from titles.models import Season


class MovieTmdb(BaseTmdb):
    title_type = MOVIE
    imdb_id_path = 'imdb_id'

    def __init__(self, *args, **kwargs):
        # TODO: title_id in init? simpler
        super().__init__(*args, **kwargs)
        self.title_model_map.update({
            'release_date': 'release_date',
            'runtime': 'runtime',
            'name': 'title',
        })

        self.response_handlers_map.update({
            'keywords/keywords': self.save_keywords
        })

        self.urls['details'] = 'movie'


class SeriesTmdb(BaseTmdb):
    title_type = SERIES
    imdb_id_path = 'external_ids/imdb_id'
    seasons_model_map = {
        'release_date': 'air_date',
        'episodes': 'episode_count',
        'number': 'season_number',
        # "poster_path": "/xRTUb8oeQHGjyBWj7OOpkvUuvKO.jpg",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title_model_map.update({
            'release_date': 'release_date',
            'runtime': 'runtime',
            'name': 'title',
        })

        self.response_handlers_map.update({
            'keywords/results': self.save_keywords,
            'seasons': self.save_seasons
        })

        self.urls['details'] = 'tv'

    def save_seasons(self):
        for season in self.api_response['seasons']:
            season_data = {
                attr_name: season[tmdb_attr_name] for attr_name, tmdb_attr_name in self.seasons_model_map.items()
            }
            Season.objects.create(title=self.title, **season_data)


class Tmdb(TmdbResponseMixin):
    """Based on imdb_id, returns either MovieTmdb or SeriesTmdb instance"""

    def find_by_id(self, title_id):
        """
        I can either call /movie or /tv endpoint. When I have an title_id I don't know what type of title it is.
        So I tried calling first endpoint and on failure called second - 2 requests at worst to get a response.
        But the thing is, you can't call /tv with imdb_id - only tmdb_id. So I use `find` endpoint and it returns
        whether an imdb_id is a movie/series and I know its tmdb_id, so I can call any endpoint.
        """
        try:
            with open(self.source_file_path.format(title_id), 'r') as outfile:
                response = json.load(outfile)
                wrapper_class = get_tmdb_wrapper_class(response['title_type'])
                return wrapper_class(response['id'])
        except FileNotFoundError:
            response = self.get_tmdb_response('find', str(title_id), qs={'external_source': 'imdb_id'})
            if response is not None:
                movies, series = response['movie_results'], response['tv_results']
                if len(movies) == 1:
                    results, title_type = movies, MOVIE
                elif len(series) == 1:
                    results, title_type = series, SERIES
                else:
                    results, title_type = [], None

                tmdb_pk = results[0]['id']
                wrapper_class = get_tmdb_wrapper_class(title_type)
                return wrapper_class(tmdb_pk)
