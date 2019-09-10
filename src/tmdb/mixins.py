from time import sleep
import os

from shared.helpers import get_json_response, SlashDict
from titles.models import Person


class PersonMixin:

    def get_person(self, value):
        person, created = Person.objects.update_or_create(
            pk=value['id'], defaults={'name': value['name'], 'image_path': value['profile_path'] or ''}
        )
        return person


class TmdbResponseMixin:
    details_path = None
    api_key = os.environ['TMDB_API_KEY']
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
        self.api_response = self.get_tmdb_response(self.details_path, tmdb_id, qs=qs)

    def call_updater_handlers(self):
        for path, handler in self.response_handlers_map.items():
            value = self.api_response[path]
            if value:
                handler(value)