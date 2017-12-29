from time import sleep

from decouple import config

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
        return person


class TmdbResponseMixin:
    api_key = config('TMDB_API_KEY')
    urls = {
        'base': 'https://api.themoviedb.org/3/'
    }

    def __init__(self):
        self.query_string = {
            'api_key': self.api_key,
            'language': 'language=en-US'
        }
        self.api_response = None

    def get_tmdb_response(self, *path_parameters, **kwargs):
        query_string = kwargs.get('qs', {})
        query_string.update(self.query_string)
        url = self.urls['base'] + '/'.join(list(map(str, path_parameters)))
        sleep(1.5)
        response, response_url = get_json_response(url, query_string)
        if response:
            print(response_url)
            return SlashDict(response)
        return None

    def set_title_response(self, tmdb_id):
        qs = {'append_to_response': 'credits,keywords,similar,videos,images,recommendations,external_ids'}
        self.api_response = self.get_tmdb_response(self.urls['details'], tmdb_id, qs=qs)

    def call_updater_handlers(self):
        for path, handler in self.response_handlers_map.items():
            value = self.api_response[path]
            if value:
                handler(value)


class BaseTmdb(PersonMixin, TmdbResponseMixin):
    title_type = None
    imdb_id_path = None

    def __init__(self, tmdb_id=None, title=None, **kwargs):
        assert tmdb_id or title
        super().__init__()
        # maps Title model attribute names to TMDB's response
        self.title_model_map = {'overview': 'overview'}
        # maps paths in TMDB's response to their method handlers
        self.response_handlers_map = {}

        self.get_details = kwargs.get('get_details', False)
        self.tmdb_id = tmdb_id
        self.imdb_id = None
        self.title = title

        if not self.title:
            try:
                self.title = Title.objects.get(tmdb_id=tmdb_id)
            except Title.DoesNotExist:
                pass

        if self.title:
            self.tmdb_id = self.title.tmdb_id
            self.imdb_id = self.title.imdb_id

        self.response_handlers_map.update({
            'genres': self.save_genres,
            'credits/cast': self.save_cast,
        })

    def get_or_create(self):
        if self.title:
            return self.title

        self.set_title_response(self.tmdb_id)
        if self.api_response:
            self.imdb_id = self.api_response[self.imdb_id_path]
            if self.imdb_id:
                return self.create()

        return None

    def create(self):
        title_data = self.get_basic_data()
        self.title = Title.objects.create(tmdb_id=self.tmdb_id, imdb_id=self.imdb_id, **title_data)

        self.call_updater_handlers()
        if self.get_details:
            TitleDetailsGetter(self.title).run()

        return self.title

    def update(self):
        """updates existing title - both: basic info and details"""
        if self.title:
            self.set_title_response(self.tmdb_id)
            title_data = self.get_basic_data()
            Title.objects.filter(pk=self.title.pk).update(**title_data)
            self.title.refresh_from_db()
            # if get_details won't be called, update_date won't be updated (filter.update doesn't call save)
            # self.title.save()
            self.clear_related()
            self.call_updater_handlers()
            TitleDetailsGetter(self.title).run()

    def get_basic_data(self):
        title_data = {
            attr_name: self.api_response[tmdb_attr_name] for attr_name, tmdb_attr_name in self.title_model_map.items()
        }
        title_data.update({
            'type': self.title_type,
            'image_path': self.api_response['poster_path'] or ''
        })
        return title_data

    def save_keywords(self, value):
        pks = []
        for keyword in value:
            keyword, created = Keyword.objects.get_or_create(pk=keyword['id'], defaults={'name': keyword['name']})
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

    def clear_related(self):
        """before title is updated, all of his related models must be cleared so they can be updated"""
        self.title.keywords.clear()
        self.title.genres.clear()
        CastTitle.objects.filter(title=self.title).delete()


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

    def clear_related(self):
        super().clear_related()
        CrewTitle.objects.filter(title=self.title).delete()


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

    def clear_related(self):
        super().clear_related()
        CrewTitle.objects.filter(title=self.title).delete()
        Season.objects.filter(title=self.title).delete()


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
        wrapper_class, tmdb_id = self.call_find_endpoint(imdb_id)
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


class TitleDetailsGetter(TmdbResponseMixin):
    """Class that fetches additional information for a title"""

    def __init__(self, title):
        super().__init__()
        self.title = title
        print(f'TitleUpdater for {self.title.imdb_id}')

        # this is needed because similar/recommended/collection titles have the same type as self.title
        # and this instance is needed to fetch their details
        self.tmdb_instance = self.title.get_tmdb_instance()

        self.response_handlers_map = {
            'similar/results': self.save_similar,
            'recommendations/results': self.save_recommendations,
            'belongs_to_collection': self.save_collection
        }

    def run(self):
        self.set_title_response(self.title.tmdb_id)
        if self.api_response:
            # title could have details. make sure they are cleared before updating them
            self.clear_details()
            self.title.before_get_details()
            self.call_updater_handlers()
            self.title.after_get_details()

    def save_similar(self, value):
        self.save_titles_to_attribute(value, self.title.similar)

    def save_recommendations(self, value):
        self.save_titles_to_attribute(value, self.title.recommendations)

    def save_collection(self, value):
        """
        Collection is updated every time. If title is in collection X, all its titles will be removed from it,
        and each title will be added again to the collection - in case some has been added/removed from it
        """
        if self.title.is_movie:
            collection, created = Collection.objects.update_or_create(pk=value['id'], defaults={'name': value['name']})
            response = self.get_tmdb_response('collection', collection.pk)
            if response is not None:
                title_pks = []
                for part in response['parts']:
                    movie = MovieTmdb(part['id']).get_or_create()
                    if movie is not None:
                        title_pks.append(movie.pk)

                collection.titles.update(collection=None)
                Title.objects.filter(pk__in=title_pks).update(collection=collection)
                # self.title just got a collection, but it needs to be refreshed
                self.title.refresh_from_db()

    def save_titles_to_attribute(self, value, attribute):
        pks = []
        for result in value:
            title = self.tmdb_instance(result['id']).get_or_create()
            if title:
                pks.append(title.pk)
        attribute.add(*pks)

    def clear_details(self):
        self.title.similar.clear()
        self.title.recommendations.clear()


class MovieTmdbTaskMixin:

    def get_instance(self, result):
        return MovieTmdb(result['id']).get_or_create()


class DailyTmdbTask(TmdbResponseMixin):
    path_parameters = ()
    attribute_name = None

    def __init__(self, model_instance):
        super().__init__()
        self.model_instance = model_instance

    def get(self):
        response = self.get_tmdb_response(*self.path_parameters)
        if response is not None:
            pks = []
            for result in response['results']:
                instance = self.get_instance(result)
                if instance:
                    pks.append(instance.pk)

            getattr(self.model_instance, self.attribute_name).add(*pks)

        return None

    def get_instance(self, *args):
        raise NotImplementedError


class PopularMoviesTmdbTask(MovieTmdbTaskMixin, DailyTmdbTask):
    path_parameters = ('movie', 'popular')
    attribute_name = 'movies'


class NowPlayingMoviesTmdbTask(MovieTmdbTaskMixin, DailyTmdbTask):
    path_parameters = ('movie', 'now_playing')
    attribute_name = 'titles'


class UpcomingMoviesTmdbTask(MovieTmdbTaskMixin, DailyTmdbTask):
    path_parameters = ('movie', 'upcoming')
    attribute_name = 'titles'


class PopularTVTmdbTask(DailyTmdbTask):
    path_parameters = ('tv', 'popular')
    attribute_name = 'tv'

    def get_instance(self, result):
        return SeriesTmdb(result['id']).get_or_create()


class PopularPeopleTmdbTask(PersonMixin, DailyTmdbTask):
    path_parameters = ('person', 'popular')
    attribute_name = 'persons'

    def get_instance(self, result):
        return self.get_person(result)


class TmdbTaskRunner:
    today = now().date()

    def run(self):
        print('run tasks', self.today)
        self.run_popular_tasks()
        self.run_other_tasks()

    def run_popular_tasks(self):
        popular = self.get_model_instance(Popular)
        if popular:
            PopularMoviesTmdbTask(popular).get()
            PopularTVTmdbTask(popular).get()
            PopularPeopleTmdbTask(popular).get()
            popular.active = True
            popular.save()

    def run_other_tasks(self):
        now_playing = self.get_model_instance(NowPlaying)
        if now_playing:
            NowPlayingMoviesTmdbTask(now_playing).get()
            now_playing.active = True
            now_playing.save()

        upcoming = self.get_model_instance(Upcoming)
        if upcoming:
            UpcomingMoviesTmdbTask(upcoming).get()
            upcoming.active = True
            upcoming.save()

    def get_model_instance(self, model):
        """only active instances can exist, so if there is no active instance from today - it means it can be created"""
        if not model.objects.filter(update_date=self.today).exists():
            return model.objects.create(update_date=self.today)
        return None
