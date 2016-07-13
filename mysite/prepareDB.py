import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

import csv
from time import strptime
from movie.models import Genre, Director, Type, Entry

def prepare_date_csv(d):                                        # MOVE IT TO NEW FILE
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
            genre_list = row['Genres'].split(', ')
            for g in row['Genres'].split(', '):
                genre = Genre.objects.get_or_create(name=g)[0]
                entry.genre.add(genre)
            for d in row['Directors'].split(', '):
                director = Director.objects.get_or_create(name=d)[0]
                entry.director.add(director)

def update():
    pass