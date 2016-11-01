import django, os
from django.db.models import Count, CharField, Value, ForeignKey
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
import re, datetime, pytz
from django.utils import timezone
from users.models import *
from recommend.models import *
from django.contrib.auth.models import User

user = User.objects.all().first()
print(user.username)


# rated_titles = Title.objects.filter(rating__user__username='test').order_by('-rating__rate_date')
# rated_titles = Title.objects.all().order_by('-rating__rate_date')
# print(rated_titles)

# titles = Title.objects.extra(select={
#     'seen_by_user': """SELECT 1 FROM movie_rating as rating
#         WHERE rating.title_id = movie_title.id AND rating.user_id = %s""",
#     'has_in_watchlist': """SELECT 1 FROM movie_watchlist as watchlist
#         WHERE watchlist.title_id = movie_title.id AND watchlist.user_id = %s AND watchlist.deleted = false""",
#     'has_in_favourites': """SELECT 1 FROM movie_favourite as favourite
#         WHERE favourite.title_id = movie_title.id AND favourite.user_id = %s"""
# }, select_params=[1] * 3)
#
# print(titles.query)
# for t in titles:
#     print(t.seen_by_user, t.has_in_watchlist, t.has_in_favourites, t.name)
#
# titles = Title.objects.filter()



# x = User.objects.annotate(num=Count('title')).order_by('-num')
# rated_titles = Title.objects.filter(rating__user=x).order_by('-rating__rate_date')
# print(x)
# print(rated_titles)

# display users with their watched titles

# Recommendation.objects.all().delete()
# x = Rating.objects.filter(user__id=1).annotate(Count('title', distinct=True)).count()
# print(x)
# x = Rating.objects.filter(user__id=1).count()
# print(x)
# print(Title.objects.all().last().rating_set.filter(user=user).values('user__username'))
# print(Rating.objects.all())
# print(Rating.objects.all().order_by('title__id').distinct('title__id'))

# x = Title.objects.extra(select={'ye': "year < %s"}, select_params=['2010'])
# x = Title.objects.extra(select={'ye': "SELECT COUNT(*) FROM movie_rating WHERE movie_rating.title_id = movie_title.id"})
# x = Title.objects.extra(select={'seen_by_user': "SELECT 1 FROM movie_rating WHERE movie_rating.title_id = movie_title.id AND movie_rating.user_id = %s",
#                                 'has_in_watchlist': "SELECT 1 FROM movie_watchlist WHERE movie_watchlist.title_id = movie_title.id AND movie_watchlist.user_id = %s"},
#                         select_params=[user.id, user.id])
# x = Title.objects.extra(select={'seen_by_user': "SELECT 1 FROM recommend_recommendation WHERE recommend_recommendation.title_id = movie_title.id AND recommend_recommendation.user_id = %s"}, select_params=[user.id])
# x = Title.objects.all()#.order_by('-id')
# print(x.count())
# for a in x:
#     print(a.seen_by_user, a.has_in_watchlist, a.name)




# followed_by_user = UserFollow.objects.filter(user_follower=user).values_list('user_followed', flat=True)
# followed_who_saw_this_title = Rating.objects.filter(user__id__in=followed_by_user, title=requested_obj).values_list(
#     'user__id', flat=True)
# followed_who_have_it_in_recommended = Recommendation.objects.filter(user__id__in=followed_by_user,
#                                                                     title=requested_obj).values_list('user_id',
#                                                                                                      flat=True)
#
# 'follows': UserFollow.objects.filter(user_follower=user).exclude(
#     user_followed__id__in=followed_who_saw_this_title).exclude(
#     user_followed__id__in=followed_who_have_it_in_recommended),

# x = UserFollow.objects.filter(user_follower=1)
# title = Title.objects.get(slug='inferno-2016')
# # title = Title.objects.get(slug='ice-age-collision-course-2016')
# print([a.user_followed.username for a in x if not Recommendation.objects.filter(user=a.user_followed, title=title).exists()
#        and not Rating.objects.filter(user=a.user_followed, title=title).exists()])


from chart.charts import count_for_month_lists
# print(count_for_month_lists(2016, 'test'))
# x = Title.objects.all().annotate(col=Value('xx', output_field=ForeignKey(User)))
# for a in x:
#     print(a.col)
# print(Rating.objects.all().last().title_set.all())
# x = Recommendation.objects.filter(added_date__date=datetime.date.today())
# print(x)
# print(x.added_date > datetime.datetime.today())

# def get_users_ratings_from_rss():
#     for user in User.objects.all(imdb_imdb_ratings__null=False, used=False):
#         update_from_rss(user)
# user = User.objects.filter(username='admin')[0]
# UserProfile.objects.filter(user=user).update(imdb_id='ur44264813')
# profile, created = UserProfile.objects.update_or_create(user=user)


# title = Title.objects.get(const='tt3165612')
# Rating.objects.create(user=user, title=title, rate=7, rate_date=datetime(2016, 5, 4))
# x = Rating.objects.filter(user=user, title=title, rate=7)

# user = profile
# Watchlist.objects.filter(user=user).delete()
# x = convert_to_datetime('Wed, 26 Oct 2016 12:51:04 GMT', 'xml') + timedelta(hours=7)
# print(x)
# print(x.tzinfo)
# print(timezone.now())
# print(timezone.now().tzinfo)
#
# # utc = pytz.timezone('US/Pacific')
# utc = pytz.timezone('UTC')
# x = x.replace(tzinfo=utc)
# print(x)
# y = Watchlist.objects.get(id=8)
# print('rss:', x)
# print('db:', y.added_date)
# print(x > y.added_date)

# print(x.astimezone(utc))
# a = Watchlist.objects.get(id='437')
# b = Watchlist.objects.get(id='438')
# b.added_date = datetime(2016, 10, 16, 18, 18, 9)
# b.save()
# print(a.added_date, a.added_date > b.added_date, b.added_date)
# update_from_csv(user)
# update_from_rss(user)
# get_watchlist(user)
# print(timezone.now())
# from django.utils.dateparse import parse_datetime
# naive = parse_datetime("2016-10-16 09:24:09")
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

# x = Rating.objects.filter(user__id=1)
# print(x)
# x = Rating.objects.filter(user__id=1).title_set.all()
# print(x)
# print(user)
# print(user.userprofile)
# print(user.userprofile.imdb_ratings)