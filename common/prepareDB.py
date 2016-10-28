import csv
import os
import sys
from .utils import prepare_json
from mysite.settings.base import MEDIA_ROOT
from .prepareDB_utils import convert_to_datetime, get_rss, get_omdb, unpack_from_rss_item, get_and_assign_poster
from django.contrib.auth.models import User
from movie.models import Title, Type, Genre, Actor, Director, Watchlist, Rating


def get_title_data(const):
    json = get_omdb(const)
    if json:
        json = prepare_json(json)
        print('get_title_data, adding:', json['Title'])
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
        return True
    return False


def get_title_or_create(const):
    if not Title.objects.filter(const=const).exists():
        is_added = get_title_data(const)
        if not is_added:
            return False
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
            obj, created = Watchlist.objects.get_or_create(user=user, title=title, added_date=date, imdb=True)
            if created:
                print('get_watchlist', user, title, date)
            # if not user_watchlist.filter(title=title, added_date=date, imdb=True).exists():
            #     Watchlist.objects.create(user=user, title=title, added_date=date, imdb=True)

        to_delete = [x for x in user_watchlist.filter(imdb=True).exclude(title__const__in=current_watchlist)
                     if not x.is_rated_with_later_date]
        for obj in to_delete:
            print('deleting', obj.title, obj.added_date)
            # obj.delete()


# this should be done only once per user! WHEN it has been uploaded
# BOOLEAN FIELD if it has been successfull. it'd great if not using omdbapi... but fuck it
# there should be option to not include ratings.csv and only use RSS - so only provide your profil url / imdb id
# need validate csv
# this can be only done when there are no ratings
# need time sleep or something.
# valid imdb_id

def update_from_csv(user):
    path = os.path.join(MEDIA_ROOT, str(user.userprofile.imdb_ratings))
    if os.path.isfile(path):
        print('update_from_csv:', user)
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for num, row in enumerate(reader):
                title = get_title_or_create(row['const'])
                rate_date = convert_to_datetime(row['created'], 'csv')
                obj, created = Rating.objects.get_or_create(user=user, title=title, rate_date=rate_date)
                if created:
                    obj.rate = row['You rated']
                    obj.save(update_fields=['rate'])


def update_from_rss(user):
    itemlist = get_rss(user.userprofile.imdb_id, 'ratings')
    if itemlist:
        print('update_from_rss:', user)
        for num, obj in enumerate(itemlist):
            const, rate, rate_date = unpack_from_rss_item(obj)
            title = get_title_or_create(const)
            obj, created = Rating.objects.get_or_create(user=user, title=title, rate_date=rate_date)
            if created:
                obj.rate = rate
                obj.save(update_fields=['rate'])
            if num > 10:
                break


def update_users_ratings_from_rss():
    for user in User.objects.filter(userprofile__imdb_id__isnull=False):
        update_from_rss(user)


def update_users_ratings_from_csv():
    for user in User.objects.exclude(userprofile__imdb_ratings=''):
        update_from_csv(user)


def update_users_watchlist():
    for user in User.objects.filter(userprofile__imdb_id__isnull=False):
        get_watchlist(user)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        command = sys.argv[1]
        if command == 'allrss':
            update_users_ratings_from_rss()
        if command == 'allcsv':
            update_users_ratings_from_csv()
        if command == 'allwatchlist':
            update_users_watchlist()
