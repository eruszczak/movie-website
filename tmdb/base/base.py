import json
import os
from decouple import config
from django.conf import settings

from shared.helpers import SlashDict, get_json_response
from titles.constants import TITLE_CREW_JOB
from titles.models import CastTitle, Person, Genre, CastCrew, Title, Keyword


class TmdbResponseMixin:
    api_key = config('TMDB_API_KEY')
    source_file_path = os.path.join(settings.BACKUP_ROOT, 'source', '{}.json')

    def __init__(self, *args, **kwargs):
        self.query_string = {
            'api_key': self.api_key,
            'language': 'language=en-US'
        }

    def get_tmdb_response(self, *path_parameters, **kwargs):
        query_string = kwargs.get('qs', {})
        query_string.update(self.query_string)
        url = self.urls['base'] + '/'.join(path_parameters)
        response = get_json_response(url, query_string)
        return response or SlashDict(response)


class BaseTmdb(TmdbResponseMixin):
    title_type = None
    title = None
    api_response = None
    query_string = {}
    imdb_id_path = None

    # maps Title model attribute names to TMDB's response
    title_model_map = {
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

    def __init__(self, tmdb_id):
        super().__init__()
        self.tmdb_id = tmdb_id

        self.response_handlers_map.update({
            'genres': self.save_genres,
            'credits/cast': self.save_cast,
            'credits/crew': self.save_crew,
            # 'similar/results': self.save_similar
        })

    def save(self):
        title_data = {
            attr_name: self.api_response[tmdb_attr_name] for attr_name, tmdb_attr_name in self.title_model_map.items()
        }

        title_data.update({
            'imdb_id': self.get_imdb_id_from_response(),
            'type': self.title_type,
            'source': self.api_response
        })

        self.title = Title.objects.create(tmdb_id=self.tmdb_id, **title_data)
        self.save_posters()

        for path, handler in self.response_handlers_map.items():
            path_value = self.api_response[path]
            handler(path_value)

        return self.title

    def get_imdb_id_from_response(self):
        return self.api_response[self.imdb_id_path]

    def delete(self):
        print(self.title.delete())

    def update(self):
        pass

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

    # def save_similar(self):
    #     pks = []
    #     for result in self.api_response['similar']['results']:
    #         similar_title = TMDB().get_title(str(result['id']), False)
    #         pks.append(similar_title.pk)
    #     self.title.similar.add(*pks)

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

    def get_title(self):
        try:
            return Title.objects.get(tmdb_id=self.tmdb_id)
        except Title.DoesNotExist:
            pass

        qs = {
            'append_to_response': 'credits,keywords,similar,videos,images,recommendations,external_ids'
        }
        self.api_response = self.get_tmdb_response(self.urls['details'], str(self.tmdb_id), qs=qs)
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