import json
import os
from time import sleep

from decouple import config
from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify

from django.utils.timezone import now

from shared.helpers import get_json_response, SlashDict
from titles.constants import MOVIE, SERIES, CREATOR, TITLE_CREW_JOB
from titles.models import Season, Person, CrewTitle, Popular, Title, Keyword, Genre, CastTitle, Collection, NowPlaying, \
    Upcoming


class PersonMixin:

    def get_person(self, value):
        person, created = Person.objects.update_or_create(
            pk=value['id'], defaults={'name': value['name'], 'image_path': value['profile_path'] or ''}
        )
        # if not person.slug:
        #     # person doesnt have a slug so I have to get details about that person to check alternative names
        #     person_details = self.get_tmdb_response('person', value['id'])
        #     if person_details is not None:
        #         aka = person_details['also_known_as']
        #         for other_name in aka:
        #             if slugify(other_name):
        #                 person.name = other_name
        #                 person.save()
        #                 break
        return person


class TmdbResponseMixin:
    api_key = config('TMDB_API_KEY')
    source_file_path = os.path.join(settings.BACKUP_ROOT, 'source', '{}.json')
    urls = {
        'base': 'https://api.themoviedb.org/3/'
    }

    def __init__(self):
        self.query_string = {
            'api_key': self.api_key,
            'language': 'language=en-US'
        }

    def get_tmdb_response(self, *path_parameters, **kwargs):
        query_string = kwargs.get('qs', {})
        query_string.update(self.query_string)
        url = self.urls['base'] + '/'.join(list(map(str, path_parameters)))
        response = get_json_response(url, query_string)
        print(response.get('name'), response.get('title'), url)
        if response is None:
            return None
        return SlashDict(response)

    def get_response_from_file(self, title_id):
        with open(self.source_file_path.format(title_id), 'r') as outfile:
            return SlashDict(json.load(outfile))

    def save_to_file(self, data, file_name):
        with open(self.source_file_path.format(file_name), 'w') as outfile:
            json.dump(data, outfile)


class BaseTmdb(PersonMixin, TmdbResponseMixin):
    title_type = None
    title = None
    api_response = None
    query_string = {}
    imdb_id_path = None
    cached_response = False

    # maps Title model attribute names to TMDB's response
    title_model_map = {
        'overview': 'overview',
        'image_path': 'poster_path'
    }

    # maps paths in TMDB's response to their method handlers
    response_handlers_map = {}

    def __init__(self, tmdb_id, title=None, **kwargs):
        # todo: decide about limits
        if not settings.DEBUG:
            sleep(2)
        super().__init__()
        self.call_updater = kwargs.get('call_updater', False)
        self.cached_response = kwargs.get('cached_response', None)
        self.tmdb_id = tmdb_id

        if not title:
            try:
                self.title = Title.objects.get(tmdb_id=tmdb_id)
            except Title.DoesNotExist:
                pass

        self.response_handlers_map.update({
            'genres': self.save_genres,
            'credits/cast': self.save_cast,
        })

        print(self.tmdb_id, 'updated', self.call_updater)

    def get_or_create(self):
        if self.title:
            print('title existed', self.title.name)

            # self.save_cast(self.cached_response['credits/cast'])
            # self.save_crew(self.cached_response['credits/crew'])
            return self.title

        # This is for testing. Because once title in production is added, I won't need this file anymore.
        if self.cached_response:
            self.api_response = self.cached_response
            return self.create()

        try:
            # it's 'cached_response' but not from TmdbWrapper
            self.api_response = self.get_response_from_file(self.tmdb_id)
        except FileNotFoundError:
            qs = {'append_to_response': 'credits,keywords,similar,videos,images,recommendations,external_ids'}
            self.api_response = self.get_tmdb_response(self.urls['details'], self.tmdb_id, qs=qs)
            self.api_response['title_type'] = self.title_type

            if self.api_response:
                imdb_id = self.get_imdb_id_from_response()
                for id_value in [imdb_id, self.tmdb_id]:
                    self.save_to_file(self.api_response, id_value)

        if self.api_response:
            return self.create()

        return None

    def create(self):
        title_data = {
            attr_name: self.api_response[tmdb_attr_name] for attr_name, tmdb_attr_name in self.title_model_map.items()
        }

        title_data.update({
            'imdb_id': self.get_imdb_id_from_response(),
            'type': self.title_type,
            'source': self.api_response
        })

        self.title = Title.objects.create(tmdb_id=self.tmdb_id, **title_data)
        # update_or_create

        for path, handler in self.response_handlers_map.items():
            value = self.api_response[path]
            if value:
                handler(value)

        if self.call_updater:
            TitleUpdater(self.title)
            # self.title.update()

        return self.title

    def get_imdb_id_from_response(self):
        return self.api_response[self.imdb_id_path]

    def save_keywords(self, value):
        pks = []
        for keyword in value:
            keyword, created = Keyword.objects.get_or_create(pk=keyword['id'], defaults={'name': keyword})
            pks.append(keyword.pk)
        self.title.keywords.add(*pks)

    def save_genres(self, value):
        pks = []
        for genre in value:
            genre, created = Genre.objects.get_or_create(pk=genre['id'], defaults={'name': genre['name']})
            pks.append(genre.pk)
        self.title.genres.add(*pks)

    def save_cast(self, value):
        for cast in value:
            person = self.get_person(cast)
            CastTitle.objects.create(title=self.title, person=person, character=cast['character'], order=cast['order'])


class MovieTmdb(BaseTmdb):
    title_type = MOVIE
    imdb_id_path = 'imdb_id'
    model_map = {
        'release_date': 'release_date',
        'runtime': 'runtime',
        'name': 'title',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls['details'] = 'movie'
        self.title_model_map.update(self.model_map)
        self.response_handlers_map.update({
            'keywords/keywords': self.save_keywords,
            'credits/crew': self.save_crew
        })

    def save_crew(self, value):
        for crew in value:
            job = TITLE_CREW_JOB.get(crew['job'])
            if job:
                person = self.get_person(crew)
                CrewTitle.objects.create(title=self.title, person=person, job=job)


class SeriesTmdb(BaseTmdb):
    title_type = SERIES
    imdb_id_path = 'external_ids/imdb_id'
    model_map = {
        'release_date': 'first_air_date',
        'name': 'name',
    }
    seasons_model_map = {
        'release_date': 'air_date',
        'episodes': 'episode_count',
        'number': 'season_number',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls['details'] = 'tv'
        self.title_model_map.update(self.model_map)
        self.response_handlers_map.update({
            'keywords/results': self.save_keywords,
            'seasons': self.save_seasons,
            'created_by': self.save_created_by
        })

    def save_seasons(self, value):
        for season in value:
            season_data = {
                attr_name: season[tmdb_attr_name] for attr_name, tmdb_attr_name in self.seasons_model_map.items()
            }
            Season.objects.create(title=self.title, **season_data)

    def save_created_by(self, value):
        for creator in value:
            person, created = Person.objects.get_or_create(pk=creator['id'], defaults={'name': creator['name']})
            CrewTitle.objects.create(title=self.title, person=person, job=CREATOR)


def get_tmdb_concrete_class(title_type):
    """depending on title_type, returns MovieTmdb or SeriesTmdb class"""
    if title_type == MOVIE:
        return MovieTmdb
    elif title_type == SERIES:
        return SeriesTmdb
    return None


class TmdbWrapper(TmdbResponseMixin):
    """Based on imdb_id, returns either MovieTmdb or SeriesTmdb instance"""

    def get(self, imdb_id, **kwargs):
        """
        I can either call /movie or /tv endpoint. When I have an title_id I don't know what type of title it is.
        So I tried calling first endpoint and on failure called second - 2 requests at worst to get a response.
        But the thing is, you can't call /tv with imdb_id - only tmdb_id. So I use `find` endpoint and it returns
        whether an imdb_id is a movie/series and I know its tmdb_id, so I can call any endpoint.
        """
        try:
            cached_response = self.get_response_from_file(imdb_id)
            tmdb_id = cached_response['id']
            wrapper_class = get_tmdb_concrete_class(cached_response['title_type'])
        except FileNotFoundError:
            wrapper_class, tmdb_id = self.call_find_endpoint(imdb_id)
        else:
            kwargs.update(cached_response=cached_response)

        if wrapper_class:
            return wrapper_class(tmdb_id, **kwargs).get_or_create()

        return None

    def call_find_endpoint(self, title_id):
        response = self.get_tmdb_response('find', title_id, qs={'external_source': 'imdb_id'})
        if response is not None:
            movies, series = response['movie_results'], response['tv_results']
            if len(movies) == 1:
                results, title_type = movies, MOVIE
            elif len(series) == 1:
                results, title_type = series, SERIES
            else:
                return None, None

            return get_tmdb_concrete_class(title_type), results[0]['id']

        return None


class TitleUpdater(TmdbResponseMixin):
    """Class that fetches additional information for a title"""

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.api_response = SlashDict(title.source)
        self.tmdb_instance = get_tmdb_concrete_class(title.type)

        self.response_handlers_map = {
            'similar/results': self.save_similar,
            'recommendations/results': self.save_recommendations
        }
        if self.title.is_movie:
            self.response_handlers_map.update({
                'belongs_to_collection': self.save_collection,
            })

        for path, handler in self.response_handlers_map.items():
            value = self.api_response[path]
            if value:
                handler(value)

    def save_similar(self, value):
        self.save_titles_to_attribute(value, self.title.similar)

    def save_recommendations(self, value):
        self.save_titles_to_attribute(value, self.title.recommendations)

    def save_collection(self, value):
        if self.title.is_movie:
            collection, created = Collection.objects.get_or_create(pk=value['id'], defaults={'name': value['name']})
            response = self.get_tmdb_response('collection', collection.pk)
            if response is not None:
                title_pks = []
                for part in response['parts']:
                    movie = MovieTmdb(part['id']).get_or_create()
                    if movie is not None:
                        title_pks.append(movie.pk)

                collection.titles.update(collection=None)
                Title.objects.filter(pk__in=title_pks).update(collection=collection)

    def save_titles_to_attribute(self, value, attribute):
        pks = []
        for result in value:
            title = self.tmdb_instance(result['id']).get_or_create()
            if title:
                pks.append(title.pk)
        attribute.add(*pks)


class DailyTmdbTask(TmdbResponseMixin):
    path_parameters = ()
    today = now().date()
    model = None
    attribute_name = None

    def get(self):
        response = self.get_tmdb_response(*self.path_parameters)
        if response is not None:
            obj, created = self.model.objects.get_or_create(update_date=self.today)
            attribute = getattr(obj, self.attribute_name)
            if not attribute.count():
                pks = []
                for result in response['results']:
                    instance = self.get_instance(result)
                    if instance:
                        pks.append(instance.pk)
                attribute.add(*pks)
            return obj

        return None

    def get_instance(self, *args):
        raise NotImplementedError


class PopularMoviesTmdbTask(DailyTmdbTask):
    path_parameters = ('movie', 'popular')

    def get_instance(self, result):
        return MovieTmdb(result['id']).get_or_create()


class PopularPeopleTmdbTask(PersonMixin, DailyTmdbTask):
    path_parameters = ('person', 'popular')

    def get_instance(self, result):
        return self.get_person(result)


class NowPlayingMoviesTmdbTask(DailyTmdbTask):
    path_parameters = ('movie', 'now_playing')

    def get_instance(self, result):
        return MovieTmdb(result['id']).get_or_create()


class UpcomingMoviesTmdbTask(DailyTmdbTask):
    path_parameters = ('movie', 'upcoming')

    def get_instance(self, result):
        return MovieTmdb(result['id']).get_or_create()


class PopularTV(DailyTmdbTask):
    path_parameters = ('tv', 'popular')

    def get_instance(self, result):
        return SeriesTmdb(result['id']).get_or_create()
