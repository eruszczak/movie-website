from datetime import datetime

from django.db.models import F
from django.contrib.auth.models import User
from recommend.models import Recommendation
from ..models import Watchlist, Favourite, Rating

from common.prepareDB_utils import validate_rate


def toggle_title_in_watchlist(user, title, watch=None, unwatch=None):
    watchlist_instance = Watchlist.objects.filter(user=user, title=title).first()
    if watch is not None:
        if watchlist_instance and watchlist_instance.imdb:
            # this is when you delete title imdb=True and then you add it again
            watchlist_instance.deleted = False
            watchlist_instance.save(update_fields=['deleted'])
        else:
            Watchlist.objects.create(user=user, title=title)
    elif unwatch is not None:
        if watchlist_instance.imdb:
            watchlist_instance.deleted = True
            watchlist_instance.save(update_fields=['deleted'])
        else:
            watchlist_instance.delete()


def toggle_title_in_favourites(user, title, fav=None, unfav=None):
    user_favourites = Favourite.objects.filter(user=user)
    if fav is not None:
        Favourite.objects.create(user=user, title=title, order=user_favourites.count() + 1)
    elif unfav is not None:
        favourite_instance = user_favourites.filter(title=title).first()
        user_favourites.filter(order__gt=favourite_instance.order).update(order=F('order') - 1)
        favourite_instance.delete()


def recommend_title(title, sender, usernames):
    users = []
    message = ''
    for username in usernames:
        user = User.objects.filter(username=username).first()
        if user:
            is_rated = Rating.objects.filter(user=user, title=title).exists()
            is_recommended = Recommendation.objects.filter(user=user, title=title).exists()
            if not is_recommended and not is_rated:
                Recommendation.objects.create(user=user, sender=sender, title=title)
                users.append(user)
    if users:
        message = 'You recommended <a href="{}">{}</a> to '.format(title.get_absolute_url(), title.name)
        message += ', <a href="{}">{}</a>'.join([(user.userprofile.get_absolute_url(), user.username) for user in users])
    return message


def create_or_update_rating(title, user, rate, insert_as_new=False):
    today = datetime.now().date()
    current_rating = Rating.objects.filter(user=user, title=title).first()
    todays_rating = Rating.objects.filter(user=user, title=title, rate_date=today)
    if validate_rate(rate) and title:
        if current_rating and not insert_as_new:
            current_rating.rate = rate
            current_rating.save(update_fields=['rate'])
        elif insert_as_new and todays_rating.exists():
            todays_rating.update(rate=rate)
        else:
            Rating.objects.create(user=user, title=title, rate=rate, rate_date=today)
    elif rate == '0' and title and current_rating:
        # this is for 'cancel' button in Raty. It deletes current rating
        current_rating.delete()
