import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

import csv
from time import strptime
from movie.models import Genre, Director, Type, Entry, Archive

import json
import urllib.request
import xml.etree.ElementTree as ET

def prepare_date_csv(d):                                                                    # MOVE IT TO NEW FILE
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

def prepare_date2_xml_released(date):
    '07 Aug 2015 -> 2015-08-07'
    month = str(strptime(date[3:6], '%b').tm_mon)
    month = '0' + month if len(month) == 1 else month
    new_date = '{}-{}-{}'.format(date[-4:], month, date[:2])
    return new_date

def csvTOdb():              # fname.isfile()
    fname = 'ratings.csv'
    with open(fname, 'r') as f:
        reader = csv.DictReader(f)
        for num, row in enumerate(reader):
            if Entry.objects.filter(const=row['const']).exists():   # if this Entry exists, add to History, update & skip
                continue
            type = Type.objects.get_or_create(name=row['Title type'])[0]
            rate_date = convert_date(row['created'])
            entry = Entry(const=row['const'], name=row['Title'], type=type, rate=row['You rated'], rate_imdb=row['IMDb Rating'],
                          rate_date=rate_date, runtime=row['Runtime (mins)'], year=row['Year'], votes=row['Num. Votes'],
                          release_date=row['Release Date (month/day/year)'], url_imdb=row['URL'])
            entry.save()    # no need for save() if p = Person.objects.create()
            for g in row['Genres'].split(', '):
                genre = Genre.objects.get_or_create(name=g)[0]
                entry.genre.add(genre)
            for d in row['Directors'].split(', '):
                director = Director.objects.get_or_create(name=d)[0]
                entry.director.add(director)

def getRSS(user='ur44264813'):                                                              # LET USERS CREATE OWN ACCOUNT
    try:
        req = urllib.request.urlopen('http://rss.imdb.com/user/{}/ratings'.format(user))
    except:
        print('rss error')
        return False
    return ET.fromstring(req.read())

def getOMDb(imdbID):
    try:
        req = urllib.request.urlopen('http://www.omdbapi.com/?i={}&plot=full&type=true&tomatoes=true&r=json'.format(imdbID))
    except:
        print('omdb error')
        return False
    return json.loads(req.read().decode('utf-8'))

def update():
    'from rss xml: const, rate and rate_date. Then use const to get info from omdbapi json'
    xml = getRSS()
    if not xml:
        return
    itemlist = xml.findall('channel/item')
    for i, obj in enumerate(itemlist, 1):
        const = obj.find('link').text[-10:-1]
        rate = obj.find('description').text.strip()[-2:-1]
        rate_date = prepare_date_xml(obj.find('pubDate').text)
        url_imdb = 'http://www.imdb.com/title/{}/'.format(const)
        json = getOMDb(const)
        if json and json['Response']:
            if Entry.objects.filter(const=const).exists():
                entry = Entry.objects.get(const=const)
                archive = Archive.objects.create(const=entry.const, rate=entry.rate, rate_date=entry.rate_date,
                                                 id_old=entry.id, name=entry.name)
                entry.delete()
                # print(entry.name)
                # make copy of this object and delete it. below compare this copy and new entry (to make sure api worked)
                continue
            types = {'movie': Type.objects.get(name='Feature Film'), 'series': Type.objects.get(name='TV Series')}
            type_of_entry = types['movie']
            for t, t_obj in types.items():
                if t == json['Type']:
                    type_of_entry = t_obj
            entry = Entry(const=const, name=json['Title'], type=type_of_entry, rate=rate, rate_imdb=json['imdbRating'],
                        rate_date=rate_date, runtime=json['Runtime'][:-4], year=json['Year'], votes=json['imdbVotes'],
                        release_date=prepare_date2_xml_released(json['Released']), url_imdb=url_imdb,
                        url_poster=json['Poster'], tomato_user_meter=json['tomatoUserMeter'],
                        tomato_user_rate=json['tomatoUserRating'], tomato_user_reviews=json['tomatoUserReviews'],
                        tomatoConsensus=json['tomatoConsensus'], url_tomato=json['tomatoURL'], plot=json['Plot'],
                        inserted_by_updater=True
                        )
            entry.save()
            genres = list(map(str.lower, json['Genre'].replace('Sci-Fi', 'sci_fi').split(', ')))
            for g in genres:
                genre = Genre.objects.get_or_create(name=g)[0]
                entry.genre.add(genre)
            for d in json['Director'].split(', '):
                director = Director.objects.get_or_create(name=d)[0]
                entry.director.add(director)
            if i > 10:
                print('heh')
                return

# update()

# think about RESETing db and then fill it again but OMDB API FOR each entry
# http://www.omdbapi.com/?i=tt0944947&Season=7 GET season nr first then get info for each season (released, title)
# series: function? what about models

archive={}
for y in Entry.objects.order_by('-year').values('year').distinct():
    archive[y['year']] = Entry.objects.filter(year=y['year']).count()
    # print(Entry.objects.filter(year=y.year).count()
    # print(y['y'])
