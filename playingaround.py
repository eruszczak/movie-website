from datetime import timedelta
from time import sleep

import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from django.db.models import Q, Subquery, OuterRef

import pytz
from django.contrib.auth import get_user_model
from importer.utils import import_ratings_from_csv, export_ratings
from tmdb.mixins import TmdbResponseMixin
from tmdb.popular import PopularMoviesTmdbTask, TmdbPopularTaskRunner
from tmdb.api import MovieTmdb, TmdbWrapper, TitleDetailsGetter
import sys
from django.utils.timezone import now

from mysite.settings import MEDIA_ROOT
from api.mixins import GetTitleMixin, GetUserMixin
from lists.models import Favourite

User = get_user_model()
user = User.objects.all().first()

collection_id = 119

from titles.models import Title, Person, Collection, Upcoming, Popular, NowPlaying, CurrentlyWatchingTV, CastTitle, \
    CrewTitle, Season, Keyword


export_ratings(user)



def remove_attrs(imdb_id=None):
    imdb_id = imdb_id or 'tt2527336'
    t = Title.objects.get(imdb_id=imdb_id)

    keyword = t.keywords.all().first()
    t.keywords.remove(keyword)
    similar = t.similar.all().first()
    t.similar.remove(similar)
    recommendations = t.recommendations.all().first()
    t.recommendations.remove(recommendations)

    t.collection =None
    t.update_date = t.update_date - timedelta(days=1)
    t.save()

    print(t.keywords.all().count(), t.keywords.all())
    print(t.similar.all().count(), t.similar.all())
    print(t.recommendations.all().count(), t.recommendations.all())
    # print(t.collection, t.collection.titles.count(), t.collection.titles.all())
    print(t.update_date)

# remove_attrs()

def test_updater():
    imdb_id = 'tt2527336'  # 2003
    # TmdbWrapper().get(imdb_id=imdb_id, update=True)

    t = Title.objects.get(imdb_id=imdb_id)

    keyword = t.keywords.all().first()
    t.keywords.remove(keyword)
    similar = t.similar.all().first()
    t.similar.remove(similar)
    recommendations = t.recommendations.all().first()
    t.recommendations.remove(recommendations)

    t.collection =None
    t.save()

    print(t.keywords.all().count(), t.keywords.all())
    print(t.similar.all().count(), t.similar.all())
    print(t.recommendations.all().count(), t.recommendations.all())
    print(t.collection, t.collection.titles.count(), t.collection.titles.all())
    print(t.update_date)

    # t.update()
    # sleep(3)
    # t.refresh_from_db()
    #
    # print(t.keywords.all().count(), t.keywords.all())
    # print(t.similar.all().count(), t.similar.all())
    # print(t.recommendations.all().count(), t.recommendations.all())
    # print(t.collection, t.collection.titles.count(), t.collection.titles.all())
    # print(t.update_date)

# test_updater()


# def random_date():
#     start = datetime(2010, 1, 1, tzinfo=pytz.utc)
#     end = datetime.now(tz=pytz.utc)
#     return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))
#
#
# def get_random_title():
#     idtitle = random.randint(1, Title.objects.count())
#     return Title.objects.filter(id=idtitle).first()
#
#
# def get_random_rated_title(user):
#     titles = Title.objects.filter(rating__user=user).values_list('const', flat=True).distinct()
#     return Title.objects.get(const=random.choice(titles))
#
#
# def get_random_recommended_title(user):
#     titles = Title.objects.filter(watchlist__user=user).values_list('const', flat=True).distinct()
#     return Title.objects.get(const=random.choice(titles))
#
# def get_random_user(user):
#     us = User.objects.exclude(username=user.username).values_list('id', flat=True)
#     return User.objects.get(id=random.choice(us))


# for i in range(15):
#     # better nicknames?
#     username = 'dummy' + str(i)
#     password = '123123'
#     user, created = User.objects.get_or_create(username=username)
#     user.set_password(password)
#     user.save()
#
#     if not Rating.objects.filter(user=user).exists():
#         r = random.randint(0, random.randint(1, 1000))
#         r2 = random.randint(0, random.randint(1, 120))
#         r3 = random.randint(0, random.randint(1, 200))
#         r4 = random.randint(0, random.randint(1, 200))
#         r5 = random.randint(0, random.randint(1, 10))
#
#         for j in range(r):
#             rate = random.randint(1, 10)
#             title = get_random_title()
#             if title:
#                 d = random_date()
#                 if not Rating.objects.filter(user=user, title=title, rate_date=d).exists():
#                     Rating.objects.get_or_create(user=user, title=title, rate=rate, rate_date=d)
#
#         for j in range(r2):
#             title = get_random_title()
#             if title:
#                 d = random_date()
#                 if not Favourite.objects.filter(user=user, title=title).exists():
#                     Favourite.objects.get_or_create(user=user, title=title, added_date=d)
#
#         for j in range(r3):
#             title = get_random_title()
#             if title:
#                 d = random_date()
#                 if not Watchlist.objects.filter(user=user, title=title).exists():
#                     Watchlist.objects.get_or_create(user=user, title=title, added_date=d)
#
#         for j in range(r4):
#             title = get_random_rated_title(user)
#             if title:
#                 d = random_date()
#                 rate = random.randint(1, 10)
#                 if not Rating.objects.filter(user=user, title=title, rate_date=d).exists():
#                     Rating.objects.get_or_create(user=user, title=title, rate=rate, rate_date=d)
#
#         for j in range(r5):
#             u = get_random_user(user)
#             UserFollow.objects.get_or_create(user_follower=user, user_followed=u)
#         # recommend titles to followed (they should not be unrecommended when the user is deleted)
#
#     # else:
#     #     Rating.objects.filter(user=user).delete()

