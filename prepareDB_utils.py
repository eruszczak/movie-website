import os
import requests
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET
from movie.models import Title
from django.core.files import File
from mysite.settings import MEDIA_ROOT, BASE_DIR


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
        name = obj.find('title').text
        return const, name, date
    rate = obj.find('description').text.strip()[-3:-1].lstrip()
    return const, rate, date


# def download_posters():
#     folder = os.path.join(BASE_DIR, 'movie', 'static', 'img', 'posters')
#     for obj in Title.objects.all():
#         title = obj.const + '.jpg'
#         img_path = os.path.join(folder, title)
#         if obj.url_poster == 'N/A':
#             url = 'http://placehold.it/300x440'
#         else:
#             url = obj.url_poster
#         if not os.path.isfile(img_path):
#             try:
#                 urllib.request.urlretrieve(url, img_path)
#                 print('downloading', obj.name, title)
#             except Exception as e:
#                 print('cant download poster', obj.name, e, type(e))
#                 pass


# def download_poster(const, url):
#     folder = os.path.join(BASE_DIR, 'static', 'img', 'posters')
#     title = const + '.jpg'
#     img_path = os.path.join(folder, title)
#     if url == 'N/A':
#         url = 'http://placehold.it/300x440'
#     if not os.path.isfile(img_path):
#         try:
#             urllib.request.urlretrieve(url, img_path)
#             print('downloading', const, title)
#         except Exception as e:
#             print('cant download poster', const, e, type(e))
#             pass


def get_and_assign_poster(obj):
    title = obj.slug + '.jpg'
    try:
        img = urllib.request.urlretrieve(obj.url_poster)[0]
    except Exception as e:
        print(e, type(e))
    else:
        print(title, 'saving poster')
        obj.img.save(title, File(open(img, 'rb')), save=True)


# def assign_existing_posters(obj=None):
#     if not obj:
#         objs = Title.objects.filter(img='')
#     else:
#         objs = [obj]
#     for obj in objs:
#         print(obj.name)
#         title = obj.slug + '.jpg'
#         save_location = os.path.join(MEDIA_ROOT, title)
#         if os.path.isfile(save_location):
#             obj.img = './' + title
#             obj.save()
#             print('assigned missing poster:', title)

