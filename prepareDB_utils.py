import os
import json
import urllib.request
from time import strptime
from datetime import datetime
import xml.etree.ElementTree as ET
from movie.models import Entry
from django.core.files import File
from mysite.settings import MEDIA_ROOT, BASE_DIR


def prepare_date_csv(d):
    'Sat Nov 12 00:00:00 1993 -> 1993-11-12'
    num_to_month_name = str(strptime(d[4:7], '%b').tm_mon)
    if len(num_to_month_name) == 1:
        num_to_month_name = '0' + num_to_month_name
    new_d = '{}-{}-{}'.format(d[-4:], num_to_month_name, d[8:10].replace(' ', '0'))
    return new_d


def prepare_date_xml(date):
    'Sat, 30 Apr 2016 00:00:00 GMT -> 2016-04-30'
    month = str(strptime(date[8:11], '%b').tm_mon)
    month = '0' + month if len(month) == 1 else month
    new_date = '{}-{}-{}'.format(date[12:16], month, date[5:7])
    return new_date


def prepare_date_json(date):
    '07 Aug 2015 -> 2015-08-07'
    month = str(strptime(date[3:6], '%b').tm_mon)
    month = '0' + month if len(month) == 1 else month
    new_date = '{}-{}-{}'.format(date[-4:], month, date[:2])
    return new_date


def convert_to_datetime(date):
    try:
        # for xml (updating)
        return datetime.strptime(date, '%a, %d %b %Y %H:%M:%S GMT')
    except ValueError:
        # for csv (initial)
        return datetime.strptime(date, '%a %b %d 00:00:00 %Y')


def get_rss(user='ur44264813', source='ratings'):
    try:
        req = urllib.request.urlopen('http://rss.imdb.com/user/{}/{}'.format(user, source))
    except:
        print('rss error')
        return False
    return ET.fromstring(req.read()).findall('channel/item')


def extract_values_from_rss_item(obj, for_watchlist=False):
    const = obj.find('link').text[-10:-1]
    date = convert_to_datetime(obj.find('pubDate').text)
    if for_watchlist:
        name = obj.find('title').text
        return const, name, date
    rate = obj.find('description').text.strip()[-3:-1].lstrip()
    return const, rate, date


def get_omdb(const, api='http://www.omdbapi.com/?i={}&plot=full&type=true&tomatoes=true&r=json'):
    try:
        req = urllib.request.urlopen(api.format(const))
    except:
        print('omdb error')
        return False
    return json.loads(req.read().decode('utf-8'))


def download_posters():
    folder = os.path.join(BASE_DIR, 'movie', 'static', 'img', 'posters')
    for obj in Entry.objects.all():
        title = obj.const + '.jpg'
        img_path = os.path.join(folder, title)
        if obj.url_poster == 'N/A':
            url = 'http://placehold.it/300x440'
        else:
            url = obj.url_poster
        if not os.path.isfile(img_path):
            try:
                urllib.request.urlretrieve(url, img_path)
                print('downloading', obj.name, title)
            except:
                print('cant download poster', obj.name)
                pass


def download_poster(const, url):
    folder = os.path.join(BASE_DIR, 'static', 'img', 'posters')
    title = const + '.jpg'
    img_path = os.path.join(folder, title)
    if url == 'N/A':
        url = 'http://placehold.it/300x440'
    if not os.path.isfile(img_path):
        try:
            urllib.request.urlretrieve(url, img_path)
            print('downloading', const, title)
        except:
            print('cant download poster', const)
            pass


def download_and_save_img(obj):
    title = obj.slug + '.jpg'
    save_location = os.path.join(MEDIA_ROOT, title)
    print(save_location)
    if obj.img:
        print('title has assigned poster')
        return
    if os.path.isfile(save_location):
        obj.img = './' + title
        obj.save()
        return
    try:
        print(title, 'downloading poster')
        img = urllib.request.urlretrieve(obj.url_poster)[0]
    except Exception as e:
        print(e, type(e))
    else:
        obj.img.save(title, File(open(img, 'rb')), save=True)


def assign_existing_posters(obj=None):
    if not obj:
        objs = Entry.objects.filter(img='')
    else:
        objs = [obj]
    for obj in objs:
        print(obj.name)
        title = obj.slug + '.jpg'
        save_location = os.path.join(MEDIA_ROOT, title)
        if os.path.isfile(save_location):
            obj.img = './' + title
            obj.save()
            print('assigned missing poster:', title)

