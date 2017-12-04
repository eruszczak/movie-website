import json

from shared.helpers import SlashDict
from tmdb.base.base import TmdbResponseMixin, BaseTmdb
from titles.constants import MOVIE, SERIES, CREATOR
from titles.models import Season, Person, CastCrew, Collection


class MovieTmdb(BaseTmdb):
    title_type = MOVIE
    imdb_id_path = 'imdb_id'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title_model_map.update({
            'release_date': 'release_date',
            'runtime': 'runtime',
            'name': 'title',
        })

        self.response_handlers_map.update({
            'keywords/keywords': self.save_keywords,
            'belongs_to_collection': self.save_collection
        })

        self.urls['details'] = 'movie'

    def save_collection(self, value):
        collection_id = value.get('id')
        if collection_id is not None:
            response = self.get_tmdb_response('collection', collection_id)
            if response is not None:
                collection, created = Collection.objects.get_or_create(pk=collection_id)
                title_ids = []
                for title in response['parts']:
                    movie = MovieTmdb(title['id']).get_title_or_create()
                    title_ids.append(movie.pk)
                collection.titles.add(title_ids)


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
            'release_date': 'first_air_date',
            'name': 'name',
        })

        self.response_handlers_map.update({
            'keywords/results': self.save_keywords,
            'seasons': self.save_seasons,
            'created_by': self.save_created_by
        })

        self.urls['details'] = 'tv'

    def save_seasons(self, value):
        for season in value:
            season_data = {
                attr_name: season[tmdb_attr_name] for attr_name, tmdb_attr_name in self.seasons_model_map.items()
            }
            Season.objects.create(title=self.title, **season_data)

    def save_created_by(self, value):
        for creator in value:
            person, created = Person.objects.get_or_create(pk=creator['id'], defaults={'name': creator['name']})
            CastCrew.objects.create(title=self.title, person=person, job=CREATOR)


def get_tmdb_wrapper_class(title_type):
    """depending on title_type, returns MovieTmdb or SeriesTmdb class"""
    if title_type == MOVIE:
        return MovieTmdb
    elif title_type == SERIES:
        return SeriesTmdb
    return None


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
                response = SlashDict(json.load(outfile))
                wrapper_class = get_tmdb_wrapper_class(response['title_type'])
                print('from file')
                return wrapper_class(response['id'], cached_response=response)
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
