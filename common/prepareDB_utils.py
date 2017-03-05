import os
import pytz
import requests
import urllib.request
from json import JSONDecodeError
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

from django.core.files import File
from movie.models import Type, Genre, Actor, Director, Title
from mysite.settings import MEDIA_ROOT


def prepare_json(json):
    json['imdbVotes'] = json['imdbVotes'].replace(',', '')
    json['Runtime'] = json['Runtime'][:-4] if json['Runtime'] != 'N/A' else None
    json['Year'] = json['Year'][:4] if json['Year'] != 'N/A' else None
    for k, v in json.items():
        if v == 'N/A' and k not in ['Genre', 'Director', 'Actors']:
            json[k] = None
    return json


def convert_to_datetime(date_string, source):
    date_formats = {
        'xml': '%a, %d %b %Y %H:%M:%S GMT',
        'csv': '%a %b %d 00:00:00 %Y',
        'json': '%d %b %Y'
    }
    if date_string and date_formats.get(source):
        return datetime.strptime(date_string, date_formats[source])
    return None


def get_rss(imdb_id='ur44264813', source='ratings'):
    if not imdb_id.startswith('ur') or len(imdb_id) < 5:
        return False
    r = requests.get('http://rss.imdb.com/user/{}/{}'.format(imdb_id, source))
    return ET.fromstring(r.text).findall('channel/item') if r.status_code == requests.codes.ok else False


def get_omdb(const):
    params = {'i': const, 'plot': 'full', 'type': 'true', 'tomatoes': 'true', 'r': 'json'}
    r = requests.get('http://www.omdbapi.com/', params=params)

    if r.status_code == requests.codes.ok:
        try:
            data_json = r.json()
        except JSONDecodeError:
            print('omdb err decode')
            return False
        if data_json.get('Response') == 'True':
            return data_json
    print('omdb err')
    return False


def unpack_from_rss_item(obj, for_watchlist=False):
    const = obj.find('link').text[-10:-1]
    date = convert_to_datetime(obj.find('pubDate').text, 'xml')
    if for_watchlist:
        date += timedelta(hours=8)
        date = date.replace(tzinfo=pytz.timezone('UTC'))
        name = obj.find('title').text
        return const, name, date
    rate = obj.find('description').text.strip()[-3:-1].lstrip()
    return const, rate, date


# def get_and_assign_poster(obj):
#     title = obj.const + '.jpg'
#     posters_folder = os.path.join(MEDIA_ROOT, 'poster')
#     img_path = os.path.join(posters_folder, title)
#     poster_exists = os.path.isfile(img_path)
#     if not poster_exists:
#         try:
#             img = urllib.request.urlretrieve(obj.url_poster)[0]
#         except Exception as e:
#             print(e, type(e))
#         else:
#             print(title, 'saving poster')
#             obj.img.save(title, File(open(img, 'rb')), save=True)
#     else:
#         obj.img = os.path.join('poster', title)
#         obj.save()

def get_and_assign_poster(obj):
    title = obj.const + '.jpg'
    posters_folder = os.path.join(MEDIA_ROOT, 'poster')
    img_path = os.path.join(posters_folder, title)
    poster_exists = os.path.isfile(img_path)
    if not poster_exists:
        try:
            urllib.request.urlretrieve(obj.url_poster, img_path)
        except Exception as e:
            print(e, type(e))
            return
        else:
            print(title, 'downloaded poster', title)
    else:
        print('assigned poster', title)
    obj.img = os.path.join('poster', title)
    obj.save()


def clear_relationships(title):
    title.genre.clear()
    title.actor.clear()
    title.director.clear()


def add_new_title(const, update=False):
    json = get_omdb(const)
    if json:
        json = prepare_json(json)
        title_type = Type.objects.get_or_create(name=json['Type'].lower())[0]
        print('adding title:', json['imdbID'])

        tomatoes = dict(
            tomato_meter=json['tomatoMeter'], tomato_rating=json['tomatoRating'], tomato_reviews=json['tomatoReviews'],
            tomato_fresh=json['tomatoFresh'], tomato_rotten=json['tomatoRotten'], url_tomato=json['tomatoURL'],
            tomato_user_meter=json['tomatoUserMeter'], tomato_user_rating=json['tomatoUserRating'],
            tomato_user_reviews=json['tomatoUserReviews'], tomatoConsensus=json['tomatoConsensus']
        )
        imdb = dict(
            name=json['Title'], type=title_type, rate_imdb=json['imdbRating'],
            runtime=json['Runtime'], year=json['Year'], url_poster=json['Poster'],
            release_date=convert_to_datetime(json['Released'], 'json'),
            votes=json['imdbVotes'], plot=json['Plot']
        )

        if not update:
            title = Title.objects.create(const=const, **imdb, **tomatoes)
        else:
            clear_relationships(Title.objects.get(const=const))
            title, created = Title.objects.update_or_create(const=const, defaults=dict(tomatoes, **imdb))
            print('created must be false', created)

        if title.url_poster:
            get_and_assign_poster(title)
        for genre in json['Genre'].split(', '):
            genre, created = Genre.objects.get_or_create(name=genre.lower())
            title.genre.add(genre)
        for director in json['Director'].split(', '):
            director, created = Director.objects.get_or_create(name=director)
            title.director.add(director)
        for actor in json['Actors'].split(', '):
            actor, created = Actor.objects.get_or_create(name=actor)
            title.actor.add(actor)
        return True
    return False
