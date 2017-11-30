import requests
from decouple import config
from titles.constants import TITLE_CREW_JOB, MOVIE, TITLE_MODEL_MAP
from titles.models2 import Genre, Keyword, CastTitle, Person, CastCrew, Title


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

    # def find_genres(self):
    #     response = self.get_response(['genre', 'movie', 'list'])
    #     if response is not None:
    #         for genre in response['genres']:
    #             print(genre)

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
        for key, value in self.response.items():
            print(key, value)
        title_data['type'] = title_type

        self.title = Title.objects.get_or_create(imdb_id=self.response['imdb_id'], defaults=dict(**title_data))
        # if created:
        #     self.save_keywords()
        #     self.save_posters()

    def save_keywords(self):
        for keyword in self.response['keywords']['keywords']:
            keyword = Keyword.objects.get_or_create(pk=keyword['id'], defaults={'name': keyword})
            self.title.keywords.add(keyword)

    def save_posters(self):
        for name, url in self.urls['poster'].items():
            print(name, url + self.response['poster_path'])

    def save_genres(self):
        for genre in self.response['genres']:
            genre = Genre.objects.get_or_create(pk=genre['id'], defaults={'name': genre['name']})
            self.title.genres.add(genre)

    def save_similar(self):
        for result in self.response['similar']['results']:
            # todo: not always a movie!
            similar_title = TMDB().get_movie_data(result['imdb_id'])
            self.title.similar.add(similar_title)

    def save_credits(self):
        for cast in self.response['credits']['cast']:
            person = Person.objects.get_or_create(pk=cast['id'], defaults={'name': cast['name']})
            # todo: multiple roles for one person can happen
            CastTitle.objects.get_or_create(title=self.title, person=person, defaults={
                'character': cast['character'],
                'order': cast['order']
            })

        for crew in self.response['credits']['crew']:
            person = Person.objects.get_or_create(pk=crew['id'], defaults={'name': crew['name']})
            # job: Screenplay / Director
            job = TITLE_CREW_JOB.get(crew['job'], None)
            CastCrew.objects.get_or_create(title=self.title, person=person, defaults={
                'job': job
            })

    def get_movie_data(self, imdb_id):
        self.query_string.update({
            'append_to_response': 'credits,keywords,similar,videos,images,recommendations'
            # not sure about recommendations
        })
        self.response = self.get_response(['movie', imdb_id])
        if self.response is not None:
            return self.save_title(MOVIE)
        return None

    def get_response(self, path_parameters):
        url = self.urls['base'] + '/'.join(path_parameters or [])
        r = requests.get(url, params=self.query_string)
        print(r.url)
        if r.status_code == requests.codes.ok:
            return r.json()
        print(r.text)
        return None




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