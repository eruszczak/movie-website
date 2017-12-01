import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

import requests
from decouple import config
from titles.constants import TITLE_CREW_JOB, MOVIE, TITLE_MODEL_MAP, SERIES
from titles.models import Genre, Keyword, CastTitle, Person, CastCrew, Title


class TMDB:
    api_key = config('TMDB_API_KEY')
    urls = {
        'base': 'https://api.themoviedb.org/3/',
        'poster_base': 'http://image.tmdb.org/t/p/',
        'poster': {
            'backdrop_user': 'w1920_and_h318_bestv2',
            'backdrop_title': 'w1280',
            'small': 'w185_and_h278_bestv2',
            'card': 'w500_and_h281_bestv2'
        },

        'tv_seasons': '/tv/{}/season/{}',
        'tv_episodes': '/tv/{}/season/{}/episode/{}',

        'people': '/person/{}',
        'companies': '/company/{}',
        'discover': '/discover/movie'
    }
    query_string = {}
    title = None
    response = None

    def __init__(self):
        self.query_string['api_key'] = self.api_key
        self.query_string['language'] = 'language=en-US'

    # def find_by_imdb_id(self, imdb_id):
    #     self.query_string['external_source'] = 'imdb_id'
    #     response = self.get_response(['find', imdb_id])
    #     if response is not None:
    #         for movie in response['movie_results']:
    #             for name, url in self.urls['poster'].items():
    #                 print(name, url + movie['poster_path'])
    #             for key, value in movie.items():
    #                 print(key, value)

    # def get_tv_data(self, imdb_id, seasons=False, episodes=False):
    #     response = self.get_response(['tv', imdb_id])
    #     if response is not None:
    #         print(response)
    #
    #     if seasons:
    #         response = self.get_response(['tv', imdb_id, 'season', '{}'])
    #         if response is not None:
    #             pass

    def save_title(self, title_type):
        title_data = {
            attr_name: self.response[tmdb_attr_name] for attr_name, tmdb_attr_name in TITLE_MODEL_MAP.items()
        }

        title_data.update({
            'type': title_type,
            'source': self.response
        })

        self.title = Title.objects.create(imdb_id=self.response['imdb_id'], **title_data)
        # self.save_keywords()
        # self.save_genres()
        # self.save_posters()
        # self.save_credits()
        # self.save_similar()

        return self.title

    def save_keywords(self):
        pks = []
        for keyword in self.response['keywords']['keywords']:
            keyword, created = Keyword.objects.get_or_create(pk=keyword['id'], defaults={'name': keyword})
            pks.append(keyword.pk)
        self.title.keywords.add(*pks)

    def save_posters(self):
        for poster_type, url in self.urls['poster'].items():
            poster_url = self.urls['poster_base'] + url + self.response['poster_path']
            extension = self.response['poster_path'].split('.')[-1]
            file_name = f'{poster_type}.{extension}'
            self.title.save_poster(file_name, poster_url, poster_type)

        self.title.save()

    def save_genres(self):
        pks = []
        for genre in self.response['genres']:
            genre, created = Genre.objects.get_or_create(pk=genre['id'], defaults={'name': genre['name']})
            pks.append(genre.pk)
        self.title.genres.add(*pks)

    def save_similar(self):
        pks = []
        for result in self.response['similar']['results']:
            similar_title = TMDB().get_title(str(result['id']), False)
            pks.append(similar_title.pk)
        self.title.similar.add(*pks)

    def save_credits(self):
        for cast in self.response['credits']['cast']:
            person, created = Person.objects.get_or_create(pk=cast['id'], defaults={'name': cast['name']})
            CastTitle.objects.create(title=self.title, person=person, character=cast['character'], order=cast['order'])

        for crew in self.response['credits']['crew']:
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

        # first check if title_id is a movie, then check if it is a series
        for path_parameter, title_type in [('movie', MOVIE), ('tv', SERIES)]:
            self.response, is_success = self.get_response([path_parameter, title_id])
            if is_success:
                return self.save_title(title_type)

        return None

    def get_response(self, path_parameters):
        url = self.urls['base'] + '/'.join(path_parameters or [])
        r = requests.get(url, params=self.query_string)
        print(r.url, r.text, sep='\n')
        if r.status_code == requests.codes.ok:
            return r.json(), True
        return None, False


client = TMDB()
Title.objects.filter(imdb_id='tt0120889').delete()
title = client.get_title('tt0120889')
print(title.poster_backdrop_title)
print(title.poster_backdrop_user)

# print(title.keywords)
# print(title.genres)
# print(title.cast)
# print(title.crew)
# print(title.similar)
# client = TMDB()
# client.get_movie_data('795', False)

# for title in Title.objects.all():
#     print(title.pk, title.imdb_id, title.tmdb_id)
