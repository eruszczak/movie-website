from titles.constants import MOVIE, SERIES
from titles.models import Title, Collection
from tmdb.mixins import TmdbResponseMixin
from tmdb.api import MovieTmdb, SeriesTmdb


def get_tmdb_concrete_class(title_type):
    """depending on title_type, returns MovieTmdb or SeriesTmdb class"""
    if title_type == MOVIE:
        return MovieTmdb
    elif title_type == SERIES:
        return SeriesTmdb
    return None


class TmdbWrapper(TmdbResponseMixin):
    """Based on imdb_id, returns title if exists, else MovieTmdb or SeriesTmdb instance"""

    def get(self, imdb_id, **kwargs):
        """
        I can either call /movie or /tv endpoint. When I have an title_id I don't know what type of title it is.
        So I tried calling first endpoint and on failure called second - 2 requests at worst to get a response.
        But the thing is, you can't call /tv with imdb_id - only tmdb_id. So I use `find` endpoint and it returns
        whether an imdb_id is a movie/series and I know its tmdb_id, so I can call any endpoint.
        """
        try:
            t = Title.objects.get(imdb_id=imdb_id)
        except Title.DoesNotExist:
            print('not existed')
            wrapper_class, tmdb_id = self.call_find_endpoint(imdb_id)
            print(tmdb_id)
            if wrapper_class:
                return wrapper_class(tmdb_id, **kwargs).get_or_create()
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

    def __init__(self, title):
        super().__init__()
        self.title = title
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
            title = self.tmdb_instance(result['id']).get_or_create()
            if title:
                pks.append(title.pk)
        attribute.add(*pks)

    def clear_details(self):
        self.title.similar.clear()
        self.title.recommendations.clear()