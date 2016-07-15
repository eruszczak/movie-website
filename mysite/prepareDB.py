import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

import csv
import time
from movie.models import Genre, Director, Type, Entry, Archive, Season, Episode
from prepareDB_utils import prepare_date_csv, prepare_date_xml, prepare_date_json, getRSS, getOMDb


def getSeasonsInfo(entry, totalSeasons):
    'collects for given entry (tv-show) info about episodes and seasons'
    for i in range(1, totalSeasons + 1):
        api = 'http://www.omdbapi.com/?i={}&Season='.format(entry.const) + str(i)
        json = getOMDb(entry.const, api)
        if json and json['Response'] and 'Season' in json:
            season, updated = Season.objects.update_or_create(entry=entry, number=int(json['Season']))
            # if updated:     # DO NOT UPDATE SEASONS FOR NOW AT LEAST
            #     continue
            for ep in json['Episodes']:
                episode = Episode.objects.create(season=season, const=ep['imdbID'], number=ep['Episode'],
                                                 name=ep['Title'], release_date=ep['Released'], rate_imdb=ep['imdbRating'])

def getEntryInfo(const, rate, rate_date, is_updated=False, exists=False):
    json = getOMDb(const)
    if not (json and json['Response']):   # if FAIL add to logs AND details of updater etc...
        return
    elif is_updated and exists:      # if entry exists, updater must be sure that can delete and archive it
        entry = Entry.objects.get(const=const)
        # if Archive.objects.filter(const=entry.const, rate_date=entry.rate_date).exists():
        #     return
        archive = Archive.objects.create(const=entry.const, rate=entry.rate, rate_date=entry.rate_date)
        print('updater. exists ' + entry.name)
        entry.delete()
        print('\t...and deleted')
    type, created = Type.objects.get_or_create(name=json['Type'].lower())
    url_imdb = 'http://www.imdb.com/title/{}/'.format(const)
    rel_date = prepare_date_json(json['Released']) if json['Released'] != "N/A" else 'N/A'
    entry = Entry(const=const, name=json['Title'], type=type, rate=rate, rate_imdb=json['imdbRating'],
                rate_date=rate_date, runtime=json['Runtime'][:-4], year=json['Year'][:4], votes=json['imdbVotes'],
                release_date=rel_date, url_imdb=url_imdb,
                url_poster=json['Poster'], tomato_user_meter=json['tomatoUserMeter'],
                tomato_user_rate=json['tomatoUserRating'], tomato_user_reviews=json['tomatoUserReviews'],
                tomatoConsensus=json['tomatoConsensus'], url_tomato=json['tomatoURL'], plot=json['Plot'],
                inserted_by_updater=is_updated
                )
    entry.save()
    # genres = list(map(str.lower, json['Genre'].replace('Sci-Fi', 'sci_fi').split(', ')))
    for g in json['Genre'].split(', '):
        genre, created = Genre.objects.get_or_create(name=g.lower())
        entry.genre.add(genre)
    for d in json['Director'].split(', '):
        director, created = Director.objects.get_or_create(name=d)
        entry.director.add(director)

    # if json['Type'] == 'series' and 'totalSeasons' in json:
    #     getSeasonsInfo(entry, int(json['totalSeasons']))



def csvToDatabase():              # fname.isfile()
    fname = 'ratings.csv'
    with open(fname, 'r') as f:
        reader = csv.DictReader(f)
        for num, row in enumerate(reader):
            if num > 30:
                print('stop')
                return
            if Entry.objects.filter(const=row['const']).exists():
                print('exists ' + row['Title'])
                continue
            rate_date = prepare_date_csv(row['created'])
            print(row['Title'])
            getEntryInfo(row['const'], row['You rated'], rate_date)
# csvToDatabase()



def update():
    'from rss xml: const, rate and rate_date. Then use const to get info from omdbapi json'
    itemlist = getRSS()
    if not itemlist:
        return
    for num, obj in enumerate(itemlist):
        if num > 13:
            return
        const = obj.find('link').text[-10:-1]
        rate = obj.find('description').text.strip()[-2:-1]
        rate_date = prepare_date_xml(obj.find('pubDate').text)
        if Entry.objects.filter(const=const).exists():
            if Archive.objects.filter(const=const, rate_date=rate_date).exists():
                print('wont update because its already Archived')
                continue#return
            elif Entry.objects.filter(const=const, rate_date=rate_date).exists():
                print('wont update because its the same entry')
                continue#return
            getEntryInfo(const, rate, rate_date, is_updated=True, exists=True)
            continue
        else:
            print('updater. ' + obj.find('title').text)
            getEntryInfo(const, rate, rate_date, is_updated=True)
            # time.sleep( 5 )



# update()