import django, os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
import csv
from movie.models import Genre, Director, Type, Entry, Archive, Season, Episode, Log
from prepareDB_utils import prepare_date_csv, prepare_date_xml, prepare_date_json, getRSS, getOMDb, downloadPosters, \
    downloadPoster, convert_to_datetime
from recommend.models import Recommendation
from django.utils import timezone
from django.db.models import Count
from datetime import datetime


# def get_seasons_info(entry, totalSeasons):
#     # collects for given entry (tv-show) info about episodes and seasons
#     for i in range(1, totalSeasons + 1):
#         api = 'http://www.omdbapi.com/?i={}&Season='.format(entry.const) + str(i)
#         json = getOMDb(entry.const, api)
#         if json and json['Response'] and 'Season' in json:
#             # if Season.objects.filter(entr=entry, number=i).exists():
#             #     print('{} season already exists'.format(api))
#             #     continue
#             season, updated = Season.objects.update_or_create(entry=entry, number=i)
#             if updated:     # DO NOT UPDATE SEASONS FOR NOW AT LEAST
#                 continue
#             for ep in json['Episodes']:
#                 # if Episode.objects.filter(const=ep['imdbID']).exists():
#                 #     print('{} {} already exists'.format(api, ep['imdbID']))
#                 #     continue
#                 ep, updated = Episode.objects.update_or_create(season=season, const=ep['imdbID'], number=ep['Episode'],
#                                                                name=ep['Title'], release_date=ep['Released'],
#                                                                rate_imdb=ep['imdbRating'])
#         else:
#             print('season {} {}'.format(i, api))
# # add to getEntry


# def get_tv(single_update=False, const='not_single'):
#     if not single_update:
#         entry_series = Entry.objects.filter(type=Type.objects.get(name='series').id)
#     else:
#         entry_series = Entry.objects.filter(const=const)
#     for e in entry_series:
#         json = getOMDb(e.const)
#         if not (json and json['Response']):
#             print('\t\t\tget_tv json error')
#             return
#         try:
#             totals = int(json['totalSeasons'])
#         except ValueError:
#             print('\t\t\tvalue error', json['totalSeasons'])
#             continue
#         print('\t {} seasons {}'.format(totals, e.name))
#         get_seasons_info(e, totals)
#     if not entry_series:
#         print('not found any tvshows', const)
#
#
# # get_tv()


def get_entry_info(const, rate, rate_date, log, is_updated=False, exists=False):
    json = getOMDb(const)
    if not (json and json['Response']):
        return
    elif is_updated and exists:  # if entry exists, updater must be sure that can delete and archive it
        entry = Entry.objects.get(const=const)
        archive = Archive.objects.create(const=entry.const, rate=entry.rate, rate_date=entry.rate_date)
        print('updater. exists ' + entry.name, '\t...and deleted')
        entry.delete()
        log.updated_archived += 1
        log.save()
    typ_e, created = Type.objects.get_or_create(name=json['Type'].lower())
    url_imdb = 'http://www.imdb.com/title/{}/'.format(const)
    rel_date = prepare_date_json(json['Released']) if json['Released'] != "N/A" else 'N/A'
    rate_imdb = 0 if json['imdbRating'] == 'N/A' else float(json['imdbRating'])
    entry = Entry(const=const, name=json['Title'], type=typ_e,
                  rate=rate, rate_imdb=rate_imdb,
                  runtime=json['Runtime'][:-4], year=json['Year'][:4], votes=json['imdbVotes'],
                  release_date=rel_date, rate_date=rate_date,
                  url_imdb=url_imdb, url_poster=json['Poster'], url_tomato=json['tomatoURL'],
                  tomato_user_meter=json['tomatoUserMeter'], tomato_user_rate=json['tomatoUserRating'],
                  tomato_user_reviews=json['tomatoUserReviews'], tomatoConsensus=json['tomatoConsensus'],
                  plot=json['Plot'],
                  inserted_by_updater=is_updated
                  )
    entry.save()
    downloadPoster(entry.const, entry.url_poster)
    for g in json['Genre'].split(', '):
        genre, created = Genre.objects.get_or_create(name=g.lower())
        entry.genre.add(genre)
    for d in json['Director'].split(', '):
        director, created = Director.objects.get_or_create(name=d)
        entry.director.add(director)
    log.new_inserted += 1
    log.save()

    # if json['Type'] == 'series':
    #     get_tv(single_update=True, const=const)


def csv_to_database():  # fname.isfile()
    fname = 'ratings.csv'
    log = Log.objects.create()
    with open(fname, 'r') as f:
        reader = csv.DictReader(f)
        for num, row in enumerate(reader):
            if Entry.objects.filter(const=row['const']).exists():
                print('exists ' + row['const'])
                continue
            rate_date = convert_to_datetime(row['created'])
            # print(row['Title'])
            get_entry_info(row['const'], row['You rated'], rate_date, log)


# csv_to_database()


def update():
    # from rss xml: const, rate and rate_date. Then use const to get info from omdbapi json
    itemlist = getRSS()
    log = Log.objects.create()
    if not itemlist:
        return
    i = 0
    for num, obj in enumerate(itemlist):
        i += 1
        if i > 10:
            return
        const = obj.find('link').text[-10:-1]
        rate = obj.find('description').text.strip()[-2:-1]
        rate_date = convert_to_datetime(obj.find('pubDate').text)
        if Entry.objects.filter(const=const).exists():
            if Archive.objects.filter(const=const, rate_date=rate_date).exists():
                print('wont update because its already Archived')
                i += 1
                continue
            elif Entry.objects.filter(const=const, rate_date=rate_date).exists():
                print('wont update because its the same entry')
                i += 1
                continue
            get_entry_info(const, rate, rate_date, log, is_updated=True, exists=True)
            continue
        else:
            print('updater. ' + obj.find('title').text)
            get_entry_info(const, rate, rate_date, log, is_updated=True)
            if Recommendation.objects.filter(const=const):
                recommended_has_been_rated = Recommendation.objects.get(const=const)
                recommended_has_been_rated.is_rated = True
                recommended_has_been_rated.save()
                print('recommended has been rated TRUE')
            # time.sleep( 5 )

if len(sys.argv) > 1:
    if sys.argv[1] == 'fromCSV':
        csv_to_database()
    # if sys.argv[1] == 'seasons':
    #     get_tv()
    if sys.argv[1] == 'posters':
        downloadPosters()
    if sys.argv[1] == 'update':
        update()
    sys.exit(0)

# downloadPoster('tt2975590', u)
# update()
# downloadPosters()
# u = 'http://ia.media-imdb.com/images/M/MV5BNTE5NzU3MTYzOF5BMl5BanBnXkFtZTgwNTM5NjQxODE@._V1_SX300.jpg'

# e = Entry.objects.get(const='tt0844441')
# if e.type.id == Type.objects.get(name='series').id:
#     s = Season.objects.filter(entry=e)
#     print(s.count())
#     for seas in s:
#         print(seas.number)
#         ep = Episode.objects.filter(season=seas)
#         for epis in ep:
#             print('\t', epis.number)
#     print()


# def get_seasons(imdb_id):
#     entry = Entry.objects.get(const=imdb_id)
#     seasons = Season.objects.filter(entry=entry)
#     season_episodes = []
#     for s in seasons:
#         episodes = Episode.objects.filter(season=s)
#         season_episodes.append([s.number, episodes])
#     return season_episodes
#
# context = {'episodes': get_seasons('tt0112022')}


# for i, (num, eps) in enumerate(context['episodes']):
#     check = True
#     for j in range(len(eps) - 1):
#         if eps[0].number not in (0, 1):
#             context['episodes'][i].insert(0, check)
#             break
#         num_current, num_next = int(eps[j].number), int(eps[j + 1].number)
#         if num_current + 1 != num_next:
#             check = False
#     context['episodes'][i].insert(0, check)
#
# for a, b, c in context['episodes']:
#     print(a, b)

# l = []
# for g in Genre.objects.all():
#     l.append((g.name, Entry.objects.filter(genre=g).count()))
#     # print(g.get_absolute_url())
#     # print(<a href="{}">here</a>)
#
# l = sorted(l, key=lambda x: x[1], reverse=True)
#
# for genre, value in l:
#     # print('{} {}'.format(value, genre), value)
#     print('{:<4} {}'.format(value, genre))
#
#
from django.db.models import Count
# genres = Genre.objects.all().annotate(num=Count('entry')).order_by('-num')
# for g in genres:
#     print(g.name, g.entry_set.count(), g.get_absolute_url())
#
# # entries = Entry.objects.values('rate').distinct().annotate(num=Count('rate')).order_by('rate')
# entries = Entry.objects.extra(select={'rate_int': 'CAST(rate as INTEGER)'}).annotate(num=Count('rate'))
# ent = Entry.objects.values('rate').annotate(the_count=Count('rate')).order_by('rate')
# print(sorted(ent, key=lambda x: int(x['rate'])))
# # for e in entries:
# #     print(e.rate)


# date_object = datetime.strptime(e.rate_date, '%Y-%m-%d')

# entr = Entry.objects.filter(rate_date__icontains='2016-07')
# for e in entr:
#     print(e.name)
#     print(e.rate_date)
#     date_object = datetime.strptime(e.rate_date, '%Y-%m-%d')
#     print(date_object)

# year_counter = []
# for y in Entry.objects.order_by('-year').values('year').distinct():
#     year_counter.append((y['year'], Entry.objects.filter(year=y['year']).count()))
#
# print(year_counter)
#
# ent = Entry.objects.values('year').annotate(the_count=Count('year')).order_by('-year')
# print(ent)

# ent = Entry.objects.filter(rate_date__year=2015).values_list('rate_date__month')
# print(ent)
# e = Entry.objects.filter(rate_date__year=2015).extra({'month': "MONTH(rate_date)"}).values_list('month').annotate(total_item=Count('item'))
# print(e)
# e = Entry.objects.extra(select={'month': 'extract( MONTH FROM rate_date )'}).values('month').annotate(dcount=Count('rate_date'))
# e = Entry.objects.filter(rate_date__year=2015).extra(select={'month': 'strftime("%m", rate_date)'}).values('month').annotate(dcount=Count('rate_date'))
# obj = Entry.objects.filter(rate_date__year=2015)
# obj = Entry.objects.all()
# e = obj.extra(select={'year_': 'strftime("%Y", rate_date)', 'month': 'strftime("%m", rate_date)'}, where=['year=2015']).values('month').annotate(dcount=Count('rate_date'))
# # print(e)
# for x in e:
#     print(x)
# print(sum(a['dcount'] for a in e))

# query = """SELECT COUNT(*) AS 'the_count', strftime("%%m", rate_date) as 'month'
# FROM movie_entry
# WHERE strftime("%%Y", rate_date) = %s
# GROUP BY month"""
#
# # print(e.columns)
#
# # for p in Entry.objects.raw('SELECT * FROM movie_entry WHERE name="Die Hard"'):
# #     print(p.name)
#
# from django.db import connection
# cursor = connection.cursor()
# cursor.execute(query, [str('2015')])
# # total_rows = cursor.fetchone()
# print(list(cursor.fetchall()))
# print(Recommendation.objects.filter(date=datetime.now()).count())
# print(timezone.now().today())
# print(datetime.today())

#
# from django.utils.text import slugify
# for e in Entry.objects.all():
#     e.slug = slugify('{} {}'.format(e.name, e.year))
#     e.save()

e = Entry.objects.filter(type=Type.objects.get(name='movie').id).order_by('-rate_date')[0]
print('last seen:', e.name)

e = Entry.objects.filter(type=Type.objects.get(name='series').id).order_by('-rate_date')[0]
print('last tv show:', e.name)

e = Entry.objects.filter(type=Type.objects.get(name='movie').id, rate__gte=9).order_by('-rate_date')[0]
print('last movie rated 9-10:', e.name)

# years = Entry.objects.values('year').annotate(the_count=Count('year')).order_by('-year')
# # print(years)
#
# li = []
# l = []
# for y in years:
#     print(y)
#     print()
#     print()
#     l.append(y)
#     if int(y['year']) % 10 == 0:
#         li.append(l)
#         l = []
# # print(li)
# # print(years[::-1])
# # years = sorted(li[0], key=lambda x: x['year'])
# new = []
# for y in li:
#     a = sorted(y, key=lambda x: x['year'])
#     new.append(a)
# print(new)

# print((lambda x, f: [y for y in years in f(x))(years,)]))

