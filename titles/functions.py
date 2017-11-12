from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import F
from recommend.models import Recommendation
from titles.models import Watchlist, Favourite, Rating

User = get_user_model()


def toggle_title_in_watchlist(user=None, title=None, watch=None, unwatch=None, instance=None):
    """
    adds or deletes title from user's watchlist. if title comes from IMDb's watchlist, it is only marked as 'deleted',
    because it would be added again with another watchlist update anyway
    """
    watchlist_instance = Watchlist.objects.filter(user=user, title=title).first() if instance is None else instance

    if watchlist_instance and watchlist_instance.imdb:
        watchlist_instance.deleted = False if watch else True
        watchlist_instance.save(update_fields=['deleted'])
    else:
        if watch:
            Watchlist.objects.create(user=user, title=title)
        elif unwatch and watchlist_instance:
            watchlist_instance.delete()


def toggle_title_in_favourites(user, title, fav=None, unfav=None):
    """
    deletes or adds title to user's favourites while maintaining the proper order
    fav titles are ordered and when some title is being deleted, order of another titles must be updated
    """
    user_favourites = Favourite.objects.filter(user=user)
    if fav:
        Favourite.objects.create(user=user, title=title, order=user_favourites.count() + 1)
    elif unfav:
        favourite_instance = user_favourites.filter(title=title).first()
        user_favourites.filter(order__gt=favourite_instance.order).update(order=F('order') - 1)
        favourite_instance.delete()


def recommend_title(title, sender, usernames):
    """
    user recommends the title to list of usernames
    """
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
        message += ', '.join(['<a href="{}">{}</a>'.format(user.get_absolute_url(), user.username) for user in users])
    return message


def create_or_update_rating(title, user, rate, insert_as_new=False):
    """
    updates current title rating or creates new one
    if rate is '0' rating is deleted
    """
    today = datetime.now().date()
    current_rating = Rating.objects.filter(user=user, title=title).first()
    todays_rating = Rating.objects.filter(user=user, title=title, rate_date=today)
    if title:
        if current_rating and not insert_as_new:
            current_rating.rate = rate
            current_rating.save(update_fields=['rate'])
            return 'Updated rating'
        elif insert_as_new and todays_rating.exists():
            todays_rating.update(rate=rate)
            return 'Updated today\'s rating'
        else:
            Rating.objects.create(user=user, title=title, rate=rate, rate_date=today)
            return 'Created rating'
    elif rate == '0' and title and current_rating:
        # this is for 'cancel' button in Raty. It deletes current rating
        # todo. this should be done in another endpoint
        current_rating.delete()
        return 'Deleted rating'
