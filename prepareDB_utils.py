import json
import urllib.request
from time import strptime
import xml.etree.ElementTree as ET
import os

def prepare_date_csv(d):
    'Sat Nov 12 00:00:00 1993 -> 1993-11-12'
    monthNum_to_name = str(strptime(d[4:7], '%b').tm_mon)
    if len(monthNum_to_name) == 1:
        monthNum_to_name = '0' + monthNum_to_name
    new_d = '{}-{}-{}'.format(d[-4:], monthNum_to_name, d[8:10].replace(' ', '0'))
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


def getRSS(user='ur44264813'):
    try:
        req = urllib.request.urlopen('http://rss.imdb.com/user/{}/ratings'.format(user))
    except:
        print('rss error')
        return False
    return ET.fromstring(req.read()).findall('channel/item')


def getOMDb(imdbID, api='http://www.omdbapi.com/?i={}&plot=full&type=true&tomatoes=true&r=json'):
    try:
        req = urllib.request.urlopen(api.format(imdbID))
    except:
        print('omdb error')
        return False
    return json.loads(req.read().decode('utf-8'))


def downloadPosters():
    from movie.models import Entry
    from mysite.settings import STATIC_ROOT, BASE_DIR
    # folder = os.path.join(STATIC_ROOT, 'img', 'posters')
    folder = os.path.join(BASE_DIR, 'movie', 'static', 'img', 'posters')
    # os.makedirs(folder, exist_ok=True)
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


def downloadPoster(const, url):
    from mysite.settings import STATIC_ROOT, BASE_DIR
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
