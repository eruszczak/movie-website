from django.utils.timezone import now

from titles.models import Popular, NowPlaying, Upcoming
from tmdb.api import MovieTmdb, SeriesTmdb
from tmdb.mixins import PersonMixin, TmdbResponseMixin


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


class TmdbPopularTaskRunner:
    today = now().date()

    def run(self):
        # print('run tasks', self.today)
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
