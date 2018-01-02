from titles.constants import MOVIE, SERIES, CREATOR, TITLE_CREW_JOB
from titles.models import Season, Person, CrewTitle, Title, Keyword, Genre, CastTitle, Collection
from tmdb.mixins import PersonMixin, TmdbResponseMixin


class BaseTmdb(PersonMixin, TmdbResponseMixin):
    title_type = None
    imdb_id_path = None

    def __init__(self, tmdb_id=None, imdb_id=None, title=None, **kwargs):
        super().__init__()
        # maps paths in TMDB's response to their method handlers
        self.response_handlers_map = {
            'genres': self.save_genres,
            'credits/cast': self.save_cast
        }
        self.title_model_map = {'overview': 'overview'}  # maps Title model attribute names to TMDB's response

        # tmdb_id is not unique (tv and movie can have the same tmdb_id).
        # so if not imdb_id is passed I need to know its type
        print(tmdb_id, imdb_id, self.title_type, title)
        assert (tmdb_id and imdb_id) or (tmdb_id and self.title_type is not None) or title

        self.get_details = kwargs.get('get_details', False)
        self.title = title
        self.tmdb_id = tmdb_id
        self.imdb_id = imdb_id

        if not self.title:
            if tmdb_id and imdb_id:
                lookup = {'tmdb_id': tmdb_id, 'imdb_id': imdb_id}
            else:
                # Importer passes only tmdb_id. It's not unique, it's unique with title_type
                lookup = {'tmdb_id': tmdb_id, 'type': self.title_type}

            try:
                self.title = Title.objects.get(**lookup)
            except Title.DoesNotExist:
                pass
            else:
                print('\t\texisted!')

        if self.title:
            self.tmdb_id = self.title.tmdb_id
            self.imdb_id = self.title.imdb_id

    def get_or_create(self):
        if self.title:
            return self.title

        self.set_title_response(self.tmdb_id)
        if self.api_response:
            if self.imdb_id:
                assert self.imdb_id == self.api_response[self.imdb_id_path]

            # if getting details (eg. similar title), only tmdb_id was passed to init
            self.imdb_id = self.api_response[self.imdb_id_path]
            if self.imdb_id:
                title_data = self.get_basic_data()
                self.title = Title.objects.create(tmdb_id=self.tmdb_id, imdb_id=self.imdb_id, **title_data)
                print('created', self.title, self.title.imdb_id)

                self.call_updater_handlers()
                if self.get_details:
                    TitleDetailsGetter(self.title, api_response=self.api_response).run()

                return self.title

        return None

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
            TitleDetailsGetter(self.title, api_response=self.api_response).run()

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


def get_tmdb_concrete_class(title_type):
    """depending on title_type, returns MovieTmdb or SeriesTmdb class"""
    if title_type == MOVIE:
        return MovieTmdb
    elif title_type == SERIES:
        return SeriesTmdb
    return None


class TmdbWrapper(TmdbResponseMixin):
    """Used by importer. Based on imdb_id, returns title if exists, else MovieTmdb or SeriesTmdb instance"""

    def get(self, imdb_id, **kwargs):
        """
        I can either call /movie or /tv endpoint. When I have an title_id I don't know what type of title it is.
        So I tried calling first endpoint and on failure called second - 2 requests at worst to get a response.
        But the thing is, you can't call /tv with imdb_id - only tmdb_id. So I use `find` endpoint and it returns
        whether an imdb_id is a movie/series and I know its tmdb_id, so I can call any endpoint.
        """
        try:
            # try to find title by imdb_id, it is unique
            t = Title.objects.get(imdb_id=imdb_id)
        except Title.DoesNotExist:
            # if not exist, add new title (need to pass both ids because tmdb_id is not unique)
            wrapper_class, tmdb_id = self.call_find_endpoint(imdb_id)
            print('not existed', tmdb_id, imdb_id)
            if wrapper_class:
                return wrapper_class(imdb_id=imdb_id, tmdb_id=tmdb_id, **kwargs).get_or_create()
        else:
            print(t, 'existed')
            return t

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

    def __init__(self, title, api_response=None):
        super().__init__()
        self.title = title
        self.api_response = api_response
        print(f'TitleUpdater for {self.title.imdb_id}')

        # this is needed because similar/recommended/collection titles have the same type as self.title
        # and this instance is needed to fetch their details
        self.tmdb_instance = self.title.get_tmdb_instance()
        self.details_path = self.tmdb_instance.details_path
        self.response_handlers_map = {
            'similar/results': self.save_similar,
            'recommendations/results': self.save_recommendations,
        }
        if self.title.is_movie:
            self.response_handlers_map['belongs_to_collection'] = self.save_collection

    def run(self):
        if self.api_response is None:
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
            title = self.tmdb_instance(tmdb_id=result['id']).get_or_create()
            if title:
                pks.append(title.pk)
        attribute.add(*pks)

    def clear_details(self):
        self.title.similar.clear()
        self.title.recommendations.clear()