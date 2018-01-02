from titles.constants import MOVIE, SERIES, CREATOR, TITLE_CREW_JOB
from titles.models import Season, Person, CrewTitle, Title, Keyword, Genre, CastTitle
from tmdb.mixins import PersonMixin, TmdbResponseMixin
from tmdb.utils import TitleDetailsGetter


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
        # todo
        title_data = self.get_basic_data()
        self.title, created = Title.objects.get_or_create(
            tmdb_id=self.tmdb_id, imdb_id=self.imdb_id, defaults=dict(**title_data))
        if not created:
            print(f'{self.tmdb_id}, {self.imdb_id} --- bug. this should not exist but sometimes it does')
        print('creating')

        self.call_updater_handlers()
        if self.get_details:
            TitleDetailsGetter(self.title).run()

        return self.title

    def update(self):
        """updates existing title - both: basic info and details"""
        self.set_title_response(self.tmdb_id)
        if self.title and self.api_response:
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
    details_path = 'movie'
    title_type = MOVIE
    imdb_id_path = 'imdb_id'
    model_map = {
        'release_date': 'release_date',
        'runtime': 'runtime',
        'name': 'title',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    details_path = 'tv'
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
