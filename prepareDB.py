import django, os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
import csv
from movie.models import *
from prepareDB_utils import *
from utils.utils import email_watchlist, prepare_json


def get_title_data(const):
    json = get_omdb(const)
    if json:
        json = prepare_json(json)
        tomatoes = dict(
            tomato_meter=json['tomatoMeter'], tomato_rating=json['tomatoRating'], tomato_reviews=json['tomatoReviews'],
            tomato_fresh=json['tomatoFresh'], tomato_rotten=json['tomatoRotten'], url_tomato=json['tomatoURL'],
            tomato_user_meter=json['tomatoUserMeter'], tomato_user_rating=json['tomatoUserRating'],
            tomato_user_reviews=json['tomatoUserReviews'], tomatoConsensus=json['tomatoConsensus']
        )
        title_type = Type.objects.get_or_create(name=json['Type'].lower())[0]
        title = Title(const=const, name=json['Title'], type=title_type, rate_imdb=json['imdbRating'],
                      runtime=json['Runtime'], year=json['Year'], url_poster=json['Poster'],
                      release_date=convert_to_datetime(json['Released'], 'json'),
                      votes=json['imdbVotes'], plot=json['Plot'], **tomatoes
        )
        title.save()
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


def get_title_or_create(const):
    if not Title.objects.filter(const=const).exists():
        get_title_data(const)
    return Title.objects.get(const=const)


def get_watchlist(user):
    itemlist = get_rss(user.userprofile.imdb_id, 'watchlist')
    if itemlist:
        current_watchlist = []
        user_watchlist = Watchlist.objects.filter(user=user)
        for obj in itemlist:
            const, name, date = unpack_from_rss_item(obj, for_watchlist=True)
            title = get_title_or_create(const)
            current_watchlist.append(const)
            # Watchlist.objects.update_or_create(user=user, title=title, added_date=date, imdb=True)
            print(date)
            if not user_watchlist.filter(title=title, added_date=date, imdb=True).exists():
                print('adding to watchlist', user, title, date)
                Watchlist.objects.create(user=user, title=title, added_date=date, imdb=True)

        to_delete = [x for x in user_watchlist.filter(imdb=True).exclude(title__const__in=current_watchlist)
                     if not x.is_rated_with_later_date]
        for obj in to_delete:
            print('deleting', obj.title, obj.added_date)
            # obj.delete()

# this should be done only once per user! WHEN it has been uploaded
# BOOLEAN FIELD if it has been successfull. it'd great if not using omdbapi... but fuck it

# there should be option to not include ratings.csv and only use RSS - so only provide your profil url / imdb id
def update_from_csv(user):
    # with open(user.userprofile.imdb_id, 'r') as f:
    with open('ratings.csv', 'r') as f:
        reader = csv.DictReader(f)
        for num, row in enumerate(reader):
            title = get_title_or_create(row['const'])
            # this can be only done when there are no ratings
            rate_date = convert_to_datetime(row['created'], 'csv')
            Rating.objects.create(user=user, title=title, rate=row['You rated'], rate_date=rate_date)


# but there must be an option for updating every user and single user
def update_from_rss(user):  # maybe default suer will be admin
    itemlist = get_rss(user.userprofile.imdb_id, 'ratings')
    if itemlist:
        user_ratings = Rating.objects.filter(user=user)
        for num, obj in enumerate(itemlist):
            const, rate, rate_date = unpack_from_rss_item(obj)
            title = get_title_or_create(const)
            if not user_ratings.filter(title=title, rate=rate, rate_date=rate_date).exists():
                Rating.objects.create(user=user, title=title, rate=rate, rate_date=rate_date)
                # else:
            #     print('updater. ' + obj.find('title').text)
            #     get_entry_info(const, rate, rate_date, is_updated=True)
            #     recommended_has_been_rated = Recommendation.objects.filter(const=const)
            #     if recommended_has_been_rated:
            #         recommended_has_been_rated.update(is_rated=True)
            #         print('recommended has been rated TRUE')
                # time.sleep( 5 )

def update_users_ratings_from_rss():
    for user in User.objects.all(imdb_id__null=False):
        update_from_rss(user)

# def get_users_ratings_from_rss():
#     for user in User.objects.all(imdb_imdb_ratings__null=False, used=False):
#         update_from_rss(user)
from users.models import UserProfile
user = User.objects.filter(username='admin')[0]
# UserProfile.objects.filter(user=user).update(imdb_id='ur44264813')
# profile, created = UserProfile.objects.update_or_create(user=user)


# title = Title.objects.get(const='tt3165612')
# Rating.objects.create(user=user, title=title, rate=7, rate_date=datetime(2016, 5, 4))
# x = Rating.objects.filter(user=user, title=title, rate=7)

# user = profile
# Watchlist.objects.filter(user=user).delete()
x = convert_to_datetime('Fri, 14 Jun 2013 13:46:54 GMT', 'xml')
print(x)
a = Watchlist.objects.get(id='437')
b = Watchlist.objects.get(id='438')
b.added_date = datetime(2016, 10, 16, 18, 18, 9)
b.save()
print(a.added_date, a.added_date > b.added_date, b.added_date)
# update_from_csv(user)
# update_from_rss(user)
# get_watchlist(user)
# print(timezone.now())
# from django.utils.dateparse import parse_datetime
# naive = parse_datetime("2016-10-16 09:24:09")
import pytz
# x = pytz.timezone("Asia/Tokyo").localize(naive, is_dst=False)
# a = Watchlist.objects.filter().last()
# print(a)
# y = pytz.timezone("Europe/Warsaw").localize(a.added_date, is_dst=False)
# print(datetime.utcnow())
# print(x)
# print(y)
# print(x > y)
# now = timezone.now()
# from django.utils import timezone
# print(timezone.now())
# print(datetime.now(timezone.utc))
# print(x > now)



# print(user)
# print(user.userprofile)
# print(user.userprofile.imdb_ratings)
if len(sys.argv) > 1:
    command = sys.argv[1]
    if command == 'csv':
        update_from_csv(user)
    # elif command == 'posters':
    #     download_posters()
    elif command == 'update':
        update_from_rss(user)
        # get_watchlist()
    # elif command == 'watchlist':
    #     get_watchlist()
    # elif command == 'assign':
    #     assign_existing_posters()
    elif command == 'email':
        email_watchlist()
    # if sys.argv[1] == 'seasons':
    #     get_tv()
    sys.exit(0)