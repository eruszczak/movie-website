import django, os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
import csv
from recommend.models import Recommendation
from movie.models import *
from prepareDB_utils import *
from utils.utils import email_watchlist


def get_title_data(const):
    json = get_omdb(const)
    if json:
        title_type, created = Type.objects.get_or_create(name=json['Type'].lower())
        json['imdbVotes'] = json['imdbVotes'].replace(',', '')
        for k, v in json.items():
            if v == 'N/A' and k not in ['Genre', 'Director', 'Actors']:
                json[k] = None
        tomatoes = dict(
            tomato_meter=json['tomatoMeter'], tomato_rating=json['tomatoRating'], tomato_reviews=json['tomatoReviews'],
            tomato_fresh=json['tomatoFresh'], tomato_rotten=json['tomatoRotten'], url_tomato=json['tomatoURL'],
            tomato_user_meter=json['tomatoUserMeter'], tomato_user_rating=json['tomatoUserRating'],
            tomato_user_reviews=json['tomatoUserReviews'], tomatoConsensus=json['tomatoConsensus']
        )
        title = Title(const=const, name=json['Title'], type=title_type, rate_imdb=json['imdbRating'],
                      runtime=json['Runtime'][:-4], year=json['Year'][:4], url_poster=json['Poster'],
                      release_date=convert_to_datetime(json['Released'], 'json'),
                      votes=json['imdbVotes'], plot=json['Plot'], **tomatoes
        )
        # print(title.__dict__)
        title.save()
        download_and_save_img(title)
        for genre in json['Genre'].split(', '):
            genre, created = Genre.objects.get_or_create(name=genre.lower())
            title.genre.add(genre)
        for director in json['Director'].split(', '):
            director, created = Director.objects.get_or_create(name=director)
            title.director.add(director)
        for actor in json['Actors'].split(', '):
            actor, created = Actor.objects.get_or_create(name=actor)
            title.actor.add(actor)




# this should be done only once per user! WHEN it has been uploaded
# BOOLEAN FIELD if it has been successfull. it'd great if not using omdbapi... but fuck it

# there should be option to not include ratings.csv and only use RSS - so only provide your profil url / imdb id
def update_from_csv(user):
    # with open(user.imdb_id, 'r') as f:
    with open('ratings.csv', 'r') as f:
        reader = csv.DictReader(f)
        for num, row in enumerate(reader):
            if not Title.objects.filter(const=row['const']).exists():
                get_title_data(row['const'])
            title = Title.objects.get(const=row['const'])
            # this can be only done when there are no ratings
            rate_date = convert_to_datetime(row['created'], 'csv')
            Rating.objects.create(user=user, title=title, rate=row['You rated'], rate_date=rate_date)


# but there must be an option for updating every user and single user
def update_from_rss(user):  # maybe default suer will be admin
    itemlist = get_rss(imdb_id=user.userprofile.imdb_id, source='ratings')
    if itemlist:
        for num, obj in enumerate(itemlist):
            const, rate, rate_date = unpack_from_rss_item(obj)
            if not Title.objects.filter(const=const).exists():
                get_title_data(const)

            title = Title.objects.get(const=const)
            if not Rating.objects.filter(user=user, title=title, rate=rate, rate_date=rate_date).exists():
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
# profile, created = UserProfile.objects.update_or_create(user=user, imdb_ratings='./ratings.csv')
# user = profile
Title.objects.all().delete()
update_from_csv(user)
print(user)
print(user.userprofile)
print(user.userprofile.imdb_ratings)
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