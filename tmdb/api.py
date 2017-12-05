import json
import os

from decouple import config
from django.conf import settings

from django.utils.timezone import now

from shared.helpers import get_json_response, SlashDict
from titles.constants import MOVIE, SERIES, CREATOR, TITLE_CREW_JOB
from titles.models import Season, Person, CastCrew, Collection, Popular, Title, Keyword, Genre, CastTitle


class TmdbResponseMixin:
    api_key = config('TMDB_API_KEY')
    source_file_path = os.path.join(settings.BACKUP_ROOT, 'source', '{}.json')
    urls = {
        'base': 'https://api.themoviedb.org/3/',
        'poster_base': 'http://image.tmdb.org/t/p/',
        'poster': {
            'backdrop_user': 'w1920_and_h318_bestv2',
            'backdrop_title': 'w1280',
            'small': 'w185_and_h278_bestv2',
            'card': 'w500_and_h281_bestv2'
        }
    }

    def __init__(self, *args, **kwargs):
        self.query_string = {
            'api_key': self.api_key,
            'language': 'language=en-US'
        }

    def get_tmdb_response(self, *path_parameters, **kwargs):
        query_string = kwargs.get('qs', {})
        query_string.update(self.query_string)
        url = self.urls['base'] + '/'.join(list(map(str, path_parameters)))
        response = get_json_response(url, query_string)
        if response is None:
            return None
        return SlashDict(response)


class BaseTmdb(TmdbResponseMixin):
    title_type = None
    title = None
    api_response = None
    query_string = {}
    imdb_id_path = None
    cached_response = False

    # maps Title model attribute names to TMDB's response
    title_model_map = {
        'overview': 'overview',
        'poster_path': 'poster_path'
    }

    # maps paths in TMDB's response to their method handlers
    response_handlers_map = {}

    def __init__(self, tmdb_id, title=None, **kwargs):
        super().__init__()
        self.avoid_infinite_recursion = kwargs.get('avoid_infinite_recursion', False)
        self.tmdb_id = tmdb_id

        self.api_response = kwargs.get('cached_response')
        if self.api_response is not None:
            self.cached_response = True

        if title is None:
            try:
                self.title = Title.objects.get(tmdb_id=tmdb_id)
            except Title.DoesNotExist:
                pass

        self.response_handlers_map.update({
            # 'genres': self.save_genres,
            # 'credits/cast': self.save_cast,
            # 'credits/crew': self.save_crew,

            'similar/results': self.save_similar,
            # 'recommendations/results': self.save_recommendations
        })

    def save(self):
        title_data = {
            attr_name: self.api_response[tmdb_attr_name] for attr_name, tmdb_attr_name in self.title_model_map.items()
        }

        title_data.update({
            'imdb_id': self.get_imdb_id_from_response(),
            'type': self.title_type,
            'source': self.api_response,
        })

        self.title = Title.objects.create(tmdb_id=self.tmdb_id, **title_data)
        # self.save_posters()

        for path, handler in self.response_handlers_map.items():
            value = self.api_response[path]
            if value:
                handler(value)

        return self.title

    def get_imdb_id_from_response(self):
        return self.api_response[self.imdb_id_path]

    def delete(self):
        print(self.title.delete())

    def update(self, similar=False, recommendations=False):
        if similar:
            value = self.api_response['similar/results']
            self.save_similar(value)

        if recommendations:
            value = self.api_response['recommendations/results']
            self.save_recommendations(value)

    def save_keywords(self, value):
        pks = []
        for keyword in value:
            keyword, created = Keyword.objects.get_or_create(pk=keyword['id'], defaults={'name': keyword})
            pks.append(keyword.pk)
        self.title.keywords.add(*pks)

    def save_posters(self):
        for poster_type, url in self.urls['poster'].items():
            poster_url = self.urls['poster_base'] + url + self.api_response['poster_path']
            extension = self.api_response['poster_path'].split('.')[-1]
            file_name = f'{poster_type}.{extension}'
            self.title.save_poster(file_name, poster_url, poster_type)
        self.title.save()

    def save_genres(self, value):
        pks = []
        for genre in value:
            genre, created = Genre.objects.get_or_create(pk=genre['id'], defaults={'name': genre['name']})
            pks.append(genre.pk)
        self.title.genres.add(*pks)

    def save_similar(self, value):
        if not self.avoid_infinite_recursion:
            pks = []
            for result in value:
                similar_title = Tmdb().find_by_id(result['id'], avoid_infinite_recursion=True)
                pks.append(similar_title.pk)
            self.title.similar.add(*pks)

    def save_recommendations(self, value):
        if not self.avoid_infinite_recursion:
            pks = []
            for result in value:
                recommended_title = Tmdb().find_by_id(result['id'], avoid_infinite_recursion=True)
                pks.append(recommended_title.pk)
            self.title.recommendations.add(*pks)

    def save_cast(self, value):
        for cast in value:
            person, created = Person.objects.get_or_create(pk=cast['id'], defaults={'name': cast['name']})
            CastTitle.objects.create(title=self.title, person=person, character=cast['character'], order=cast['order'])

    def save_crew(self, value):
        for crew in value:
            person, created = Person.objects.get_or_create(pk=crew['id'], defaults={'name': crew['name']})
            job = TITLE_CREW_JOB.get(crew['job'], None)
            if job is not None:
                CastCrew.objects.create(title=self.title, person=person, job=job)

    def get_title_or_create(self):
        if self.title:
            return self.title

        if self.cached_response:
            return self.save()

        qs = {
            'append_to_response': 'credits,keywords,similar,videos,images,recommendations,external_ids'
        }
        self.api_response = self.get_tmdb_response(self.urls['details'], self.tmdb_id, qs=qs)
        if self.api_response is not None:
            imdb_id = self.get_imdb_id_from_response()
            self.api_response['title_type'] = self.title_type
            for id_value in [imdb_id, self.tmdb_id]:
                self.save_response_to_file(id_value)

            return self.save()

        return None

    def save_response_to_file(self, file_name):
        with open(self.source_file_path.format(file_name), 'w') as outfile:
            json.dump(self.api_response, outfile)
            print('created', self.source_file_path.format(file_name))


class MovieTmdb(BaseTmdb):
    title_type = MOVIE
    imdb_id_path = 'imdb_id'

    def __init__(self, *args, **kwargs):
        # self.ignore_collection = kwargs.pop('ignore_collection', False)
        super().__init__(*args, **kwargs)
        self.title_model_map.update({
            'release_date': 'release_date',
            'runtime': 'runtime',
            'name': 'title',
        })

        self.response_handlers_map.update({
            # 'keywords/keywords': self.save_keywords,
            'belongs_to_collection': self.save_collection
        })

        self.urls['details'] = 'movie'

    def save_collection(self, value):
        if not self.avoid_infinite_recursion:
            collection_id = value['id']
            response = self.get_tmdb_response('collection', collection_id)
            if response is not None:
                collection, created = Collection.objects.get_or_create(
                    pk=collection_id, defaults={'name': response['name']}
                )
                title_ids = []
                if not created:
                    collection.titles.clear()
                for title in response['parts']:
                    movie = MovieTmdb(title['id'], avoid_infinite_recursion=True).get_title_or_create()
                    if movie is not None:
                        title_ids.append(movie.pk)
                collection.titles.add(*title_ids)


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


class PopularMovies(TmdbResponseMixin):

    def get(self):
        response = self.get_tmdb_response('popular', 'movie')
        if response is not None:
            popular, created = Popular.objects.get_or_create(update_date=now().date())
            if not popular.titles.count():  # test if need .all()
                pks = []
                for result in response['results']:
                    popular_title = Tmdb().find_by_id(result['id'])
                    pks.append(popular_title.pk)
                popular.titles.add(*pks)


def get_tmdb_wrapper_class(title_type):
    """depending on title_type, returns MovieTmdb or SeriesTmdb class"""
    if title_type == MOVIE:
        return MovieTmdb
    elif title_type == SERIES:
        return SeriesTmdb
    return None


class Tmdb(TmdbResponseMixin):
    """Based on imdb_id, returns either MovieTmdb or SeriesTmdb instance"""

    def get(self, title_id, **kwargs):
        """
        I can either call /movie or /tv endpoint. When I have an title_id I don't know what type of title it is.
        So I tried calling first endpoint and on failure called second - 2 requests at worst to get a response.
        But the thing is, you can't call /tv with imdb_id - only tmdb_id. So I use `find` endpoint and it returns
        whether an imdb_id is a movie/series and I know its tmdb_id, so I can call any endpoint.
        """
        try:
            wrapper_class, cached_response = self.read_from_file(title_id)
        except FileNotFoundError:
            wrapper_class = self.call_find_endpoint(title_id)
            if wrapper_class is None:
                # sometimes `find` endpoint doesn't return anything, so I need to call `tv` or/and `movie`
                # to make sure that there are no results
                pass
        else:
            kwargs.update(cached_response=cached_response)

        return wrapper_class(title_id, **kwargs)

    def read_from_file(self, title_id):
        with open(self.source_file_path.format(title_id), 'r') as outfile:
            response = SlashDict(json.load(outfile))
            wrapper_class = get_tmdb_wrapper_class(response['title_type'])
            return wrapper_class, response

    def call_find_endpoint(self, title_id):
        response = self.get_tmdb_response('find', title_id, qs={'external_source': 'imdb_id'})
        if response is not None:
            movies, series = response['movie_results'], response['tv_results']
            if len(movies) == 1:
                results, title_type = movies, MOVIE
            elif len(series) == 1:
                results, title_type = series, SERIES
            else:
                return None

            return get_tmdb_wrapper_class(title_type)
