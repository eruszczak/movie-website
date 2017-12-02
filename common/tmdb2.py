import json
import os

import django
from django.conf import settings
from os.path import isfile

from shared.helpers import SlashDict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

import requests
from decouple import config
from titles.constants import TITLE_CREW_JOB, MOVIE, SERIES, MODEL_MAP
from titles.models import Genre, Keyword, CastTitle, Person, CastCrew, Title, Season


class TMDB:
    api_key = config('TMDB_API_KEY')
    title_type = None
    title = None
    api_response = None

    # maps Title model attribute names to TMDB's response
    title_model_map = {
        'tmdb_id': 'id',
        'overview': 'overview',
        'poster_path': 'poster_path'

    }

    # maps paths in TMDB's response to their method handlers
    response_handlers_map = {}

    urls = {
        'base': 'https://api.themoviedb.org/3/',
        'poster_base': 'http://image.tmdb.org/t/p/',
        'poster': {
            'backdrop_user': 'w1920_and_h318_bestv2',
            'backdrop_title': 'w1280',
            'small': 'w185_and_h278_bestv2',
            'card': 'w500_and_h281_bestv2'
        },

        # 'tv_seasons': '/tv/{}/season/{}',
        # 'tv_episodes': '/tv/{}/season/{}/episode/{}',

        # 'people': '/person/{}',
        # 'companies': '/company/{}',
        # 'discover': '/discover/movie'
    }

    query_string = {}

    def __init__(self):
        self.query_string['api_key'] = self.api_key
        self.query_string['language'] = 'language=en-US'

        self.response_handlers_map.update({
            'genres': self.save_genres,
            'credits/cast': self.save_cast,
            'credits/crew': self.save_crew,
            # 'similar/results': self.save_similar
        })

    def save(self, **kwargs):
        title_data = {
            attr_name: self.api_response[tmdb_attr_name] for attr_name, tmdb_attr_name in self.title_model_map.items()
        }

        title_data.update({
            'type': self.title_type,
            'source': self.api_response
        })

        self.title = Title.objects.create(imdb_id=self.api_response.get('imdb_id', kwargs['title_id']), **title_data)
        self.save_posters()
        return self.title

    def save_keywords(self):
        pks = []
        for keyword in self.api_response['keywords'].get('keywords', self.api_response['keywords']['results']):
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

    def save_genres(self):
        pks = []
        for genre in self.api_response['genres']:
            genre, created = Genre.objects.get_or_create(pk=genre['id'], defaults={'name': genre['name']})
            pks.append(genre.pk)
        self.title.genres.add(*pks)

    # def save_similar(self):
    #     pks = []
    #     for result in self.api_response['similar']['results']:
    #         similar_title = TMDB().get_title(str(result['id']), False)
    #         pks.append(similar_title.pk)
    #     self.title.similar.add(*pks)

    def save_cast(self):
        for cast in self.api_response['credits']['cast']:
            person, created = Person.objects.get_or_create(pk=cast['id'], defaults={'name': cast['name']})
            CastTitle.objects.create(title=self.title, person=person, character=cast['character'], order=cast['order'])

    def save_crew(self):
        for crew in self.api_response['credits']['crew']:
            person, created = Person.objects.get_or_create(pk=crew['id'], defaults={'name': crew['name']})
            job = TITLE_CREW_JOB.get(crew['job'], None)
            if job is not None:
                CastCrew.objects.create(title=self.title, person=person, job=job)

    def get_title(self, title_id, imdb=True):
        try:
            return Title.objects.get(**{'imdb_id' if imdb else 'tmdb_id': title_id})
        except Title.DoesNotExist:
            pass

        self.query_string.update({
            'append_to_response': 'credits,keywords,similar,videos,images,recommendations'  # TODO: not sure about recommendations
        })

        (self.api_response, is_success), title_type = self.get_title_by_imdb_id(title_id)
        if is_success:
            return self.save(title_type, title_id=title_id)

        # # first check if title_id is a movie, then check if it is a series
        # for path_parameter, title_type in [('movie', MOVIE), ('tv', SERIES)]:
        #     self.response, is_success = self.get_response([path_parameter, title_id])
        #     if is_success:
        #         return self.save_title(title_type)

        return None

    # TODO: this must work for find_by_imdb_id and normal cases
    def get_response(self, *path_parameters, imdb_id=''):
        url = self.urls['base'] + '/'.join(path_parameters or [])
        source_file_path = os.path.join(settings.BACKUP_ROOT, 'source', f'{imdb_id}.json')
        response = None

        # todo: only on imdb_id?? or always
        if isfile(source_file_path):
            with open(source_file_path, 'r') as outfile:
                return json.load(outfile), True
        else:
            r = requests.get(url, params=self.query_string)
            print(r.url, r.text, sep='\n')
            if r.status_code == requests.codes.ok:
                response = r.json()
                if imdb_id:
                    with open(source_file_path, 'w') as outfile:
                        json.dump(response, outfile)

        # if response is None:
        #     raise

        return SlashDict(response)
        # todo: what to do o failure? i dont need is_success i think just return none at least

    def delete(self):
        print(self.title.delete())

# client = TMDB()
# test_id = 'tt4574334'
# Title.objects.filter(imdb_id=test_id).delete()
# title = client.get_title(test_id)


class MovieTMDB(TMDB):
    title_type = MOVIE

    def __init__(self):
        # TODO: title_id in init? simpler
        super().__init__()
        self.title_model_map.update({
            'release_date': 'release_date',
            'runtime': 'runtime',
            'name': 'title',
        })

        self.response_handlers_map.update({
            'keywords/keywords': self.save_keywords
        })


class SeriesTMDB(TMDB):
    title_type = SERIES
    seasons_model_map = {
        'release_date': 'air_date',
        'episodes': 'episode_count',
        'number': 'season_number',
        # "poster_path": "/xRTUb8oeQHGjyBWj7OOpkvUuvKO.jpg",
    }

    def __init__(self):
        super().__init__()
        self.title_model_map.update({
            'release_date': 'release_date',
            'runtime': 'runtime',
            'name': 'title',
        })

        self.response_handlers_map.update({
            'keywords/results': self.save_keywords,
            'seasons': self.save_seasons
        })

    def save_seasons(self):
        for season in self.api_response['seasons']:
            season_data = {attr_name: season[tmdb_attr_name] for attr_name, tmdb_attr_name in self.seasons_model_map.items()}
            Season.objects.create(title=self.title, **season_data)


# TODO: i need a regular function to create proper instance?
# because I dont know if imdb_id is series i movie so I can't know what to create

# def get_title_by_imdb_id(self, imdb_id):
#     """
#     I can either call /movie or /tv endpoint. When I have an imdb_id I don't know what type of title it is.
#     So I tried calling first endpoint and on failure called second - 2 requests at worst to get a response.
#     But the thing is, you can't call /tv with imdb_id - only tmdb_id. So I use `find` endpoint and it returns
#     whether an imdb_id is a movie/series and I know its tmdb_id, so I can call any endpoint.
#     """
#     self.query_string['external_source'] = 'imdb_id'
#     response, is_success = self.get_response(['find', imdb_id], imdb_id=imdb_id)
#     if response is not None:
#         movie = response['movie_results']
#         if len(movie) == 1:
#             tmdb_pk = str(movie[0]['id'])
#             return self.get_response(['movie', tmdb_pk]), MOVIE
#
#         series = response['tv_results']
#         if len(series) == 1:
#             tmdb_pk = str(series[0]['id'])
#             return self.get_response(['tv', tmdb_pk]), SERIES
#
#         # later handle the case when TMDB doesn't have a data for a imdb_id
#         assert len(movie) == 1 or len(series) == 1
