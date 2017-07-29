import os
import requests


class TMDB:
    api_key = os.environ.get('TMDB_API_KEY')
    base_url = 'https://api.themoviedb.org/3/'
    base_poster_url = 'http://image.tmdb.org/t/p/w{}/'
    urls = {
        'base': 'https://api.themoviedb.org/3/',
        'base_poster': 'http://image.tmdb.org/t/p/w{}/',
        'tv': '/tv/{}',
        'tv_seasons': '/tv/{}/season/{}',
        'tv_episodes': '/tv/{}/season/{}/episode/{}',
        'genres': '/genre/movie/list',
        'people': '/person/{}',
        'companies': '/company/{}',

        'discover': '/discover/movie'
    }
    query_string = {}
    params = []
    poster_max_width = 200
    poster_width = {

    }
    response = None

    def __init__(self):
        self.query_string['api_key'] = self.api_key
        self.query_string['language'] = 'language=en-US'
        self.base_poster_url = self.base_poster_url.format(self.poster_max_width)

    def find(self, imdb_id):
        self.query_string['external_source'] = 'imdb_id'
        self.params = ['find', imdb_id]
        self.response = self.get_response()
        return self

    def get_response(self):
        url = self.base_url + '/'.join(self.params)
        r = requests.get(url, params=self.query_string)
        print(r.url)
        if r.status_code == requests.codes.ok:
            return r.json()
        return False

    def parse_response(self):
        if self.response is not None:
            # movies = [m['title'] for m in self.response['movie_results']]
            movies = self.response['movie_results']
            poster_paths = [m['poster_path'] for m in movies]
            poster_urls = list(map(self.get_poster_url, poster_paths))
            print(movies)
            print(poster_paths)
            print(poster_urls)

    def get_poster_url(self, url):
        return self.base_poster_url + url

client = TMDB()
client.find('tt0120889').parse_response()


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