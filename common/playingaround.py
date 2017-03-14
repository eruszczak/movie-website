import urllib.request

import django, os
import requests
from django.core.files import File

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from django.db.models import Count, CharField, Value, ForeignKey, Avg, Expression, Case, When, IntegerField
from django.contrib.auth.models import User
import re, pytz
from datetime import datetime
from django.utils import timezone
from users.models import *
from django.db.models.expressions import F
from django.db.models.aggregates import Max
from recommend.models import *
from django.shortcuts import redirect

user = User.objects.all().first()


from mysite.settings import MEDIA_ROOT
posters_path = os.path.join(MEDIA_ROOT, 'poster')
# if exists replace but never create with new name...
# img_path = os.path.join(posters_path, '500-days-of-summer-2009.jpg')
# poster_exists = os.path.isfile(img_path)
# print(poster_exists)


from common.prepareDB_utils import get_and_assign_poster


# t = Title.objects.get(const="tt0114369")
# print(t.name)
for t in Title.objects.filter(const='tt0475784'):
    # if t.const in ('tt0471019', 'tt0296554', 'tt2318453', 'tt5661770'):
    #     t.img = None
    #     t.save()
    #     print(t.img is None)
    # get_and_assign_poster(t)
    print()

# import PIL
# from PIL import Image
#
# basewidth = 120
# img = Image.open('tt0114369.jpg')
# wpercent = basewidth / float(img.size[0])
# hsize = int((float(img.size[1]) * float(wpercent)))
# img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
# img.save('tt0114369-120.jpg')




        # titles = Title.objects.extra(select={
#     'seen_by_user': """SELECT rating.rate FROM movie_rating as rating
#         WHERE rating.title_id = movie_title.id AND rating.user_id = %s LIMIT 1""",
#     'has_in_watchlist': """SELECT 1 FROM movie_watchlist as watchlist
#         WHERE watchlist.title_id = movie_title.id AND watchlist.user_id = %s AND watchlist.deleted = false""",
#     'has_in_favourites': """SELECT 1 FROM movie_favourite as favourite
#         WHERE favourite.title_id = movie_title.id AND favourite.user_id = %s"""
# }, select_params=[1] * 3)

# titles = Rating.objects.extra(select={
#     'seen_by_user': """SELECT rate FROM auth_user, movie_title
#         WHERE auth_user.id = user_id = %s AND movie_title.slug = %s LIMIT 1""",
# }, select_params=[1, 'inferno-2016'])

# followed = User.objects.extra(select={
#     'seen_by_user': """
#         SELECT
#             rating.rate
#         FROM
#             movie_rating as rating,
#             movie_title as title
#         WHERE
#             rating.title_id = title.id
#         AND
#             rating.user_id = auth_user.id
#         AND
#             title.slug = 'inferno-2016'
#         LIMIT 1""",
#     }
# )

# a = Title.objects.annotate(
#     seen_by_user=Count(
#         Case(When(rating__user__id=1, then=1), output_field=IntegerField())
#     ),
#     has_in_watchlist=Count(
#         Case(When(watchlist__user__id=1, then=1), output_field=IntegerField())
#     ),
#     has_in_favourites=Count(
#         Case(When(favourite__user__id=1, then=1), output_field=IntegerField())
#     ),
# )


# Chapters.objects.annotate(last_chapter_pk=Max('novel__chapter__pk')
#             ).filter(pk=F('last_chapter_pk'))
# def average_rating_of_title(title):
#     # avg_all_ratings = title.rating_set.values('rate').aggregate(avg=Avg('rate'))
#     sum_rate = 0
#     ids_of_users = title.rating_set.values_list('user', flat=True).order_by('user').distinct()
#     title_ratings = Rating.objects.filter(title=title)
#     for user_id in ids_of_users:
#         latest_rating = title_ratings.filter(user__id=user_id).first()
#         sum_rate += latest_rating.rate
#     if sum_rate:
#         avg_rate = round(sum_rate / len(ids_of_users), 1)
#         return '{} ({} users)'.format(avg_rate, len(ids_of_users))
#     return None

# latest_ratings_of_users = User.objects.filter(rating__title__slug='inferno-2016').annotate(current_rating=Max('rating__rate_date'), rate=F('rating__rate'))#.aggregate(a=Avg('rating__rate'))
# latest_ratings_of_users = User.objects.filter(rating__title__slug='inferno-2016').annotate(current_rating=Max('rating__rate_date')).values('rating__rate')#.aggregate(a=Avg('rating__rate'))
# # can get users/dates and manually get AVG. maybe its still better
# # av = latest_ratings_of_users.values('current_rating').aggregate(a=Avg('current_rating'))
# for rat in latest_ratings_of_users:
#     print(rat)
#

# titles = Title.objects.extra(select={
#     'seen_by_user': """SELECT rating.rate FROM movie_rating as rating
#         WHERE rating.title_id = movie_title.id AND rating.user_id = %s LIMIT 1""",
#     'has_in_watchlist': """SELECT 1 FROM movie_watchlist as watchlist
#         WHERE watchlist.title_id = movie_title.id AND watchlist.user_id = %s AND watchlist.deleted = false""",
#     'has_in_favourites': """SELECT 1 FROM movie_favourite as favourite
#         WHERE favourite.title_id = movie_title.id AND favourite.user_id = %s"""
# }, select_params=[1] * 3)


# users = User.objects.filter().extra(select={
#     'seen_by_user': """SELECT rating.rate FROM movie_rating as rating
#         WHERE rating.title_id = movie_title.id AND rating.user_id = %s LIMIT 1""",
#     'has_in_watchlist': """SELECT 1 FROM movie_watchlist as watchlist
#         WHERE watchlist.title_id = movie_title.id AND watchlist.user_id = %s AND watchlist.deleted = false""",
#     'has_in_favourites': """SELECT 1 FROM movie_favourite as favourite
#         WHERE favourite.title_id = movie_title.id AND favourite.user_id = %s"""
# }, select_params=[1] * 3)

# titles = Title.objects.annotate(
#     seen_by_user=Count(
#         Case(When(rating__user=request.user, then=1), output_field=IntegerField())
#     ),
#     has_in_watchlist=Count(
#         Case(When(watchlist__user=request.user, then=1), output_field=IntegerField())
#     ),
#     has_in_favourites=Count(
#         Case(When(favourite__user=request.user, then=1), output_field=IntegerField())
#     ),
# )

# users = UserFollow.objects.filter(user_follower=user).annotate(
#     seen_by_followed=Count(
#         Case(When(user_follower=))
#     )
# )


# from django.apps import apps
#
# a = apps.get_model('movie.Title')
# print(a.objects.all())
# print(Title)
#
# print(apps.get_models)