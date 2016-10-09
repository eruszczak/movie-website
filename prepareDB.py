import django, os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
import csv
from recommend.models import Recommendation
from movie.models import Genre, Director, Type, Entry, Archive, Log, Watchlist, Favourite
from prepareDB_utils import prepare_date_json, get_rss, get_omdb, download_posters, convert_to_datetime,\
    download_and_save_img, assign_existing_posters, extract_values_from_rss_item
from utils.utils import email_watchlist


def get_watchlist():
    itemlist = get_rss(source='watchlist')
    without_to_delete = Watchlist.objects.exclude(
        const__in=Watchlist.objects.to_delete().values_list('const', flat=True)
    )
    if itemlist:
        current_watchlist = []
        for obj in itemlist:
            const, name, date = extract_values_from_rss_item(obj, for_watchlist=True)
            current_watchlist.append(const)
            same_with_later_date = without_to_delete.filter(const=const, added_date__lt=date)
            if same_with_later_date:
                obj = same_with_later_date[0]
                print(obj.name, 'changed date', obj.added_date, date)
                obj.added_date = date
                obj.save(update_fields=['added_date'])
                continue
            if not Watchlist.objects.filter(const=const, added_date=date).exists():
                Watchlist.objects.create(const=const, name=name, added_date=date)
                print(name, 'adding to watchlist')
                continue
        to_delete = Watchlist.objects.exclude(const__in=current_watchlist)
        if to_delete:
            print(to_delete.values_list('name', flat=True), 'are no longer in Watchlist so deleting')
            to_delete.delete()


def get_entry_info(const, rate, rate_date, log, is_updated=False, exists=False):
    json = get_omdb(const)
    if json:
        if is_updated and exists:  # if entry exists, updater must be sure that can delete and archive it
            entry = Entry.objects.get(const=const)
            Archive.objects.create(const=entry.const, rate=entry.rate,
                                   rate_date=entry.rate_date, watch_again_date=entry.watch_again_date)
            print('updater. exists ' + entry.name, '\t...and deleted')
            entry.delete()
            log.updated_archived += 1
            log.save()

        title_type, created = Type.objects.get_or_create(name=json['Type'].lower())
        url_imdb = 'http://www.imdb.com/title/{}/'.format(const)
        rel_date = prepare_date_json(json['Released']) if json['Released'] != "N/A" else 'N/A'
        rate_imdb = 0 if json['imdbRating'] == 'N/A' else float(json['imdbRating'])
        entry = Entry(const=const, name=json['Title'], type=title_type,
                      rate=rate, rate_imdb=rate_imdb,
                      runtime=json['Runtime'][:-4], year=json['Year'][:4], votes=json['imdbVotes'],
                      release_date=rel_date, rate_date=rate_date,
                      url_imdb=url_imdb, url_poster=json['Poster'], url_tomato=json['tomatoURL'],
                      tomato_user_meter=json['tomatoUserMeter'], tomato_user_rate=json['tomatoUserRating'],
                      tomato_user_reviews=json['tomatoUserReviews'], tomatoConsensus=json['tomatoConsensus'],
                      plot=json['Plot'],
                      inserted_by_updater=is_updated)
        entry.save()
        download_and_save_img(entry)    # downloadPoster(entry.const, entry.url_poster)
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


def csv_to_database():
    fname = 'ratings.csv'
    log = Log.objects.create()
    with open(fname, 'r') as f:
        reader = csv.DictReader(f)
        for num, row in enumerate(reader):
            if Entry.objects.filter(const=row['const']).exists():
                print('exists ' + row['const'])
                continue
            rate_date = convert_to_datetime(row['created'])
            get_entry_info(row['const'], row['You rated'], rate_date, log)


def update():
    itemlist = get_rss()
    log = Log.objects.create()
    if itemlist:
        i = 0
        for num, obj in enumerate(itemlist):
            if i > 10:
                return  # if can't update multiple times stop it
            const, rate, rate_date = extract_values_from_rss_item(obj)
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
                recommended_has_been_rated = Recommendation.objects.filter(const=const)
                if recommended_has_been_rated:
                    recommended_has_been_rated.update(is_rated=True)
                    print('recommended has been rated TRUE')
                # time.sleep( 5 )

if len(sys.argv) > 1:
    command = sys.argv[1]
    if command == 'fromCSV':
        csv_to_database()
    elif command == 'posters':
        download_posters()
    elif command == 'update':
        update()
        get_watchlist()
    elif command == 'watchlist':
        get_watchlist()
    elif command == 'assign':
        assign_existing_posters()
    elif command == 'email':
        email_watchlist()
    # if sys.argv[1] == 'seasons':
    #     get_tv()
    sys.exit(0)


# print(sorted(Watchlist.objects.all(), key=lambda k: (k.added_date, k.get_entry)))
print(Favourite.objects.all().order_by('-order'))
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