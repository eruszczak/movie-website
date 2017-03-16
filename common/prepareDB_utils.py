import os
import pytz
import csv
import requests
import urllib.request
from json import JSONDecodeError
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import PIL
from PIL import Image

from movie.models import Type, Genre, Actor, Director, Title
from mysite.settings import MEDIA_ROOT

import logging
logger = logging.getLogger('django')


def prepare_json(json):
    json['imdbVotes'] = json['imdbVotes'].replace(',', '')
    json['Runtime'] = json['Runtime'][:-4] if json['Runtime'] != 'N/A' else None
    json['Year'] = json['Year'][:4] if json['Year'] != 'N/A' else None
    for k, v in json.items():
        if v in ('N/A', 'NA') and k not in ['Genre', 'Director', 'Actors']:
            json[k] = None
    return json


def convert_to_datetime(date_string, source):
    date_formats = {
        'xml': '%a, %d %b %Y %H:%M:%S GMT',
        'csv': '%a %b %d 00:00:00 %Y',
        'json': '%d %b %Y',
        'exported_from_db': '%Y-%m-%d'
    }
    if date_string and date_formats.get(source):
        try:
            return datetime.strptime(date_string, date_formats[source])
        except ValueError:
            return None
    return None


def validate_rate(rate):
    try:
        rate = int(rate)
    except ValueError:
        return False
    return 0 < rate < 11


def get_csv_headers(file_or_iostring):
    csv_reader = csv.reader(file_or_iostring)
    csv_headings = next(csv_reader)
    return csv_headings


def valid_csv_headers(file):
    expected_headers = ["position", "const", "created", "modified", "description", "Title", "Title type",
                        "Directors", "You rated", "IMDb Rating", "Runtime (mins)", "Year", "Genres", "Num. Votes",
                        "Release Date (month/day/year)", "URL"]
    return get_csv_headers(file) == expected_headers


def valid_imported_csv_headers(iostring):
    expected_headers = ["const", "rate_date", "rate"]
    return get_csv_headers(iostring) == expected_headers


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
            logger.exception()
            return False
        if data_json.get('Response') == 'True':
            return data_json
    logger.error('omdb wrong status code')
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
    return const, validate_rate(rate), date


def resize_image(width, img_to_resize, dest_path):
    if os.path.isfile(dest_path):
        return

    basewidth = width
    img = Image.open(img_to_resize)
    width, height = img.size
    wpercent = basewidth / float(width)
    hsize = int((float(height) * float(wpercent)))
    img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    img.save(dest_path)
    logger.info('created resized poster:' + dest_path)


def get_and_assign_poster(obj):
    title = obj.const + '.jpg'
    posters_folder = os.path.join(MEDIA_ROOT, 'poster')
    img_path = os.path.join(posters_folder, title)
    if not obj.url_poster:
        logger.info('tried to get poster but no url_poster ' + obj.const)
        return

    poster_exists = os.path.isfile(img_path)
    if not poster_exists:
        try:
            urllib.request.urlretrieve(obj.url_poster, img_path)
            logger.info('poster downloaded: ' + title)
        except (PermissionError, TypeError, ValueError) as e:
            logger.exception(e)
            return

    # here poster must exist because it already existed or was just downloaded
    obj.img = os.path.join('poster', title)
    obj.save(update_fields=['img'])

    # resized poster
    width = 120
    posters_folder_resized = os.path.join(posters_folder, str(width))
    if not os.path.exists(posters_folder_resized):
        os.mkdir(posters_folder_resized)

    img_path_resized = os.path.join(posters_folder_resized, title)
    resize_image(width, img_path, img_path_resized)
    obj.img_thumbnail = os.path.join('poster', str(width), title)
    obj.save(update_fields=['img_thumbnail'])


def clear_relationships(title):
    title.genre.clear()
    title.actor.clear()
    title.director.clear()


def add_new_title(const, update=False):
    json = get_omdb(const)
    if json:
        json = prepare_json(json)
        title_type = Type.objects.get_or_create(name=json['Type'].lower())[0]

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
            logger.info('added title:' + title.const)

        else:
            clear_relationships(Title.objects.get(const=const))
            title, created = Title.objects.update_or_create(const=const, defaults=dict(tomatoes, **imdb))
            logger.info('updated title ' + title.const)
            if created:
                logger.error('this should never happen')

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
