import requests
from decouple import config


class TMDB:
    api_key = config('TMDB_API_KEY')
    urls = {
        'base': 'https://api.themoviedb.org/3/',
        'poster': {
            'backdrop': 'http://image.tmdb.org/t/p/w1280',
            'small': 'http://image.tmdb.org/t/p/w185_and_h278_bestv2',
            'card': 'https://image.tmdb.org/t/p/w500_and_h281_bestv2',
            # 'card1': 'https://image.tmdb.org/t/p/342',
            'backdrop_user': 'https://image.tmdb.org/t/p/w1920_and_h318_bestv2'
        },

        'tv_seasons': '/tv/{}/season/{}',
        'tv_episodes': '/tv/{}/season/{}/episode/{}',

        'people': '/person/{}',
        'companies': '/company/{}',
        'discover': '/discover/movie'
    }
    query_string = {}
    poster_width = {}

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

    # def find_genres(self):
    #     response = self.get_response(['genre', 'movie', 'list'])
    #     if response is not None:
    #         for genre in response['genres']:
    #             print(genre)

    def get_movie_data(self, imdb_id):
        self.query_string.update({
            'append_to_response': 'credits,keywords,similar,videos,images,recommendations'
            # not sure about recommendations
        })
        response = self.get_response(['movie', imdb_id])
        if response is not None:
            for name, url in self.urls['poster'].items():
                print(name, url + response['poster_path'])
            for key, value in response.items():
                print(key, value)

    # def get_tv_data(self, imdb_id, seasons=False, episodes=False):
    #     response = self.get_response(['tv', imdb_id])
    #     if response is not None:
    #         print(response)
    #
    #     if seasons:
    #         response = self.get_response(['tv', imdb_id, 'season', '{}'])
    #         if response is not None:
    #             pass

    def get_response(self, path_parameters):
        url = self.urls['base'] + '/'.join(path_parameters or [])
        r = requests.get(url, params=self.query_string)
        print(r.url)
        if r.status_code == requests.codes.ok:
            return r.json()
        print(r.text)
        return None


# append_to_response
# https://developers.themoviedb.org/3/getting-started/append-to-response

# client = TMDB()
# client.find_by_imdb_id('tt0120889')
#
# client = TMDB()
# client.find_genres()

client = TMDB()
client.get_movie_data('tt0120889')

# client = TMDB()
# client.find_tv('tt4574334')

"""
search
======
let users to search new titles and they will be added to db when that happens


discover
====
show recommendations (this + similar titles of liked titles)


get details
====
cast
images(posters,backdrops, stills)
plot keywords
similar
primary info


seasons
genres
directors

https://api.themoviedb.org/3/movie/157336?api_key={api_key}&append_to_response=videos,images

"""