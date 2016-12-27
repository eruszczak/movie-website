import requests
import urllib.request
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from django.core.files import File
import pytz
from movie.models import Type, Genre, Actor, Director, Title


def prepare_json(json):
    json['imdbVotes'] = json['imdbVotes'].replace(',', '')
    json['Runtime'] = json['Runtime'][:-4] if json['Runtime'] != 'N/A' else None
    json['Year'] = json['Year'][:4] if json['Year'] != 'N/A' else None
    for k, v in json.items():
        if v == 'N/A' and k not in ['Genre', 'Director', 'Actors']:
            json[k] = None
    return json


def convert_to_datetime(date_string, source):
    if date_string is None:
        return None
    if source == 'xml':
        return datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S GMT')
    elif source == 'csv':
        return datetime.strptime(date_string, '%a %b %d 00:00:00 %Y')
    elif source == 'json':
        return datetime.strptime(date_string, '%d %b %Y')


def get_rss(imdb_id='ur44264813', source='ratings'):
    r = requests.get('http://rss.imdb.com/user/{}/{}'.format(imdb_id, source))
    return ET.fromstring(r.text).findall('channel/item') if r.status_code == requests.codes.ok else False


def get_omdb(const):
    params = {'i': const, 'plot': 'full', 'type': 'true', 'tomatoes': 'true', 'r': 'json'}
    r = requests.get('http://www.omdbapi.com/', params=params)
    data_json = r.json()
    return data_json if data_json.get('Response') == 'True' and r.status_code == requests.codes.ok else False


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


def get_and_assign_poster(obj):
    title = obj.slug + '.jpg'
    try:
        img = urllib.request.urlretrieve(obj.url_poster)[0]
    except Exception as e:
        print(e, type(e))
    else:
        print(title, 'saving poster')
        obj.img.save(title, File(open(img, 'rb')), save=True)


def get_title_data(const):
    json = get_omdb(const)
    if json:
        json = prepare_json(json)
        print('get_title_data, adding:', json['Title'])
        tomatoes = dict(
            tomato_meter=json['tomatoMeter'], tomato_rating=json['tomatoRating'], tomato_reviews=json['tomatoReviews'],
            tomato_fresh=json['tomatoFresh'], tomato_rotten=json['tomatoRotten'], url_tomato=json['tomatoURL'],
            tomato_user_meter=json['tomatoUserMeter'], tomato_user_rating=json['tomatoUserRating'],
            tomato_user_reviews=json['tomatoUserReviews'], tomatoConsensus=json['tomatoConsensus']
        )
        title_type = Type.objects.get_or_create(name=json['Type'].lower())[0]
        title = Title(
            const=const, name=json['Title'], type=title_type, rate_imdb=json['imdbRating'],
            runtime=json['Runtime'], year=json['Year'], url_poster=json['Poster'],
            release_date=convert_to_datetime(json['Released'], 'json'),
            votes=json['imdbVotes'], plot=json['Plot'], **tomatoes
        )
        title.save()
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