import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from django.db.models import Count, CharField, Value, ForeignKey, Avg, Expression, Case, When, IntegerField
from django.contrib.auth.models import User
import re, datetime, pytz
from django.utils import timezone
from users.models import *
from recommend.models import *
from movie.models import *
from django.shortcuts import redirect
user = User.objects.all().first()
print(user.username)
print(user.userprofile)
from django.conf import settings
print(settings.MEDIA_ROOT)

# rated_titles = Title.objects.filter(rating__user__username='test').order_by('-rating__rate_date')
# rated_titles = Title.objects.all().order_by('-rating__rate_date')
# print(rated_titles)

titles = Title.objects.extra(select={
    'seen_by_user': """SELECT rating.rate FROM movie_rating as rating
        WHERE rating.title_id = movie_title.id AND rating.user_id = %s LIMIT 1""",
    'has_in_watchlist': """SELECT 1 FROM movie_watchlist as watchlist
        WHERE watchlist.title_id = movie_title.id AND watchlist.user_id = %s AND watchlist.deleted = false""",
    'has_in_favourites': """SELECT 1 FROM movie_favourite as favourite
        WHERE favourite.title_id = movie_title.id AND favourite.user_id = %s"""
}, select_params=[1] * 3)
print(titles.get(slug='inferno-2016').seen_by_user)
print(redirect(user.userprofile.watchlist_url()))

profile = UserProfile.objects.get(user__username='test')
print(profile.user.username)

genres = Genre.objects.annotate(num=Count('title')).order_by('-num')
for g in genres:
    print(g.name, g.num)
# a = Title.objects.filter(rating__user__id=1).annotate(seen_by_user=Count('rating__user__id'))
# print(a.first().seen_by_user)
# print(a)

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
# print(a.query)
# print(a.first().seen_by_user)
# for t in a:
#     print(t.seen_by_user, t.has_in_watchlist, t.has_in_favourites, t.name)
#
