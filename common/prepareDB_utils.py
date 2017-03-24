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


def prepare_json(json):
    """
    parsing omdb's title data before it can be used for adding new title
    """
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
            pass
    return None


def validate_rate(rate):
    try:
        rate = int(rate)
    except (ValueError, TypeError):
        return False
    return 0 < rate < 11


def get_csv_headers(file_or_iostring):
    """
    get first line from opened csv file or iostring and return list of its csv headers
    must call seek method to restore current position to beginning of the file
    """
    csv_reader = csv.reader(file_or_iostring)
    csv_headings = next(csv_reader)
    file_or_iostring.seek(0)
    return csv_headings


def valid_csv_headers(file):
    """
    when user uploads his ratings.csv exported from IMDb, csv headers must be correct
    """
    expected_headers = ["position", "const", "created", "modified", "description", "Title", "Title type",
                        "Directors", "You rated", "IMDb Rating", "Runtime (mins)", "Year", "Genres", "Num. Votes",
                        "Release Date (month/day/year)", "URL"]
    return get_csv_headers(file) == expected_headers


def valid_imported_csv_headers(iostring):
    """
    when user imports ratings, csv headers must be the same as exported file's
    """
    expected_headers = ["const", "rate_date", "rate"]
    return get_csv_headers(iostring) == expected_headers


def get_rss(imdb_id='ur44264813', source='ratings'):
    """
    gets XML from rss.imdb.com/user/<userid>/ratings or watchlist
    """
    if not imdb_id.startswith('ur') or len(imdb_id) < 5:
        return False
    r = requests.get('http://rss.imdb.com/user/{}/{}'.format(imdb_id, source))
    return ET.fromstring(r.text).findall('channel/item') if r.status_code == requests.codes.ok else False


def get_omdb(const):
    """
    calls omdb api to get title data
    """
    params = {'i': const, 'plot': 'full', 'type': 'true', 'tomatoes': 'true', 'r': 'json'}
    r = requests.get('http://www.omdbapi.com/', params=params)

    if r.status_code == requests.codes.ok:
        try:
            data_json = r.json()
        except JSONDecodeError:
            return False

        if data_json.get('Response') == 'True':
            return data_json
    return False


def unpack_from_rss_item(obj, for_watchlist=False):
    """
    parses <item> from rss.imdb.com/user/<userid>/ratings or watchlist
    * if rating item: get title's const, rating date and rating
    * if watchlist item: get title's const and added date
    """
    const = obj.find('link').text[-10:-1]
    date = convert_to_datetime(obj.find('pubDate').text, 'xml')
    if for_watchlist:
        date += timedelta(hours=7)
        date = date.replace(tzinfo=pytz.timezone('UTC'))
        return const, date

    rate = obj.find('description').text.strip()[-3:-1].lstrip()
    assert validate_rate(rate)
    return const, date, rate


def resize_image(width, img_to_resize, dest_path):
    """
    used for making smaller version of poster (so I don't load 300x300 poster if only thumbnail is needed)
    """
    if os.path.isfile(dest_path):
        return

    basewidth = width
    img = Image.open(img_to_resize)
    width, height = img.size
    wpercent = basewidth / float(width)
    hsize = int((float(height) * float(wpercent)))
    img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    img.save(dest_path)
    print('created resized poster:' + dest_path)


def get_and_assign_poster(obj):
    """
    for given Title instance, download poster or/and reassign it. Also try to make a resized version of the poster
    """
    title = obj.const + '.jpg'
    posters_folder = os.path.join(MEDIA_ROOT, 'poster')
    img_path = os.path.join(posters_folder, title)
    if not obj.url_poster:
        print('tried to get poster but no url_poster ' + obj.const)
        return

    poster_exists = os.path.isfile(img_path)
    if not poster_exists:
        try:
            urllib.request.urlretrieve(obj.url_poster, img_path)
        except (PermissionError, TypeError, ValueError) as e:
            print(e)
            return
        print('poster downloaded: ' + title)

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
    """
    title's relations must be cleared when title is being updated
    """
    title.genre.clear()
    title.actor.clear()
    title.director.clear()


def create_m2m_relationships(title, genres=None, directors=None, actors=None):
    if genres is not None:
        for genre in genres.split(', '):
            genre, created = Genre.objects.get_or_create(name=genre.lower())
            title.genre.add(genre)
    if directors is not None:
        for director in directors.split(', '):
            director, created = Director.objects.get_or_create(name=director)
            title.director.add(director)
    if actors is not None:
        for actor in actors.split(', '):
            actor, created = Actor.objects.get_or_create(name=actor)
            title.actor.add(actor)


def add_new_title(const, update=False):
    """
    create new title or update exisiting one
    """
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

        if update:
            clear_relationships(Title.objects.get(const=const))
            title, created = Title.objects.update_or_create(const=const, defaults=dict(tomatoes, **imdb))
            print('updated title ' + title.const)
            assert not created
            # count = Title.objects.filter(const=const).update(dict(tomatoes, **imdb))
            # print(count)
            # assert count in (0, 1)
        else:
            title = Title.objects.create(const=const, **imdb, **tomatoes)
            print('added title:' + title.const)

        if title.url_poster:
            get_and_assign_poster(title)

        create_m2m_relationships(title, genres=json['Genre'], directors=json['Director'], actors=json['Actors'])

        return title
    return False
