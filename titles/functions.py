from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import F, Q

from accounts.models import UserFollow
from recommend.models import Recommendation
from titles.models import Rating, CurrentlyWatchingTV
from lists.models import Watchlist, Favourite

User = get_user_model()


def toggle_title_in_watchlist(user=None, title=None, watch=None):
    """
    adds or deletes title from user's watchlist. if title comes from IMDb's watchlist, it is only marked as 'deleted',
    because it would be added again with another watchlist update anyway
    """
    unwatch = not watch
    watchlist_instance = Watchlist.objects.filter(user=user, title=title).first()

    if watchlist_instance and watchlist_instance.imdb:
        watchlist_instance.deleted = False if watch else True
        watchlist_instance.save(update_fields=['deleted'])
        return 'Removed from watchlist'
    else:
        if watch:
            Watchlist.objects.create(user=user, title=title)
            return 'Added to watchlist'
        elif unwatch and watchlist_instance:
            watchlist_instance.delete()
            return 'Removed from watchlist'


def toggle_title_in_favourites(user, title, fav):
    """
    deletes or adds title to user's favourites while maintaining the proper order
    fav titles are ordered and when some title is being deleted, order of another titles must be updated
    """
    unfav = not fav
    user_favourites = Favourite.objects.filter(user=user)
    favourite_instance = user_favourites.filter(title=title).first()
    if fav:
        Favourite.objects.create(user=user, title=title, order=user_favourites.count() + 1)
        return 'Added to favourites'
    elif unfav and favourite_instance:
        user_favourites.filter(order__gt=favourite_instance.order).update(order=F('order') - 1)
        favourite_instance.delete()
        return 'Removed from favourites'


def recommend_title(title, sender, user_ids):
    """sender recommends the title to user_ids"""
    pks_of_followed_users = UserFollow.objects.filter(follower=sender).exclude(
        Q(followed__rating__title=title) | Q(followed__recommendation__title=title)
    ).values_list('followed__pk', flat=True)

    users = User.objects.filter(Q(pk__in=pks_of_followed_users) & Q(pk__in=user_ids))
    for user in users:
        Recommendation.objects.create(user=user, sender=sender, title=title)

    if users:
        return f'Recommended to {users.count()} users'

    return 'Already recommended'


def create_or_update_rating(title, user, rate, insert_as_new=False):
    """updates current title rating or creates new one"""
    today = datetime.now().date()
    current_rating = Rating.objects.filter(user=user, title=title).first()
    todays_rating = Rating.objects.filter(user=user, title=title, rate_date=today)
    if rate != '0':
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
    elif current_rating:
        current_rating.delete()
        return 'Deleted rating'


def follow_user(follower, followed, add):
    if add:
        UserFollow.objects.get_or_create(follower=follower, followed=followed)
        return f'Followed {followed.username}'
    else:
        UserFollow.objects.filter(follower=follower, followed=followed).delete()
        return f'Unfollowed {followed.username}'


def toggle_currently_watched_title(title, user, add):
    if add:
        CurrentlyWatchingTV.objects.get_or_create(title=title, user=user)
        return f'Watching {title.name}'
    else:
        CurrentlyWatchingTV.objects.filter(title=title, user=user).delete()
        return f'Not watching {title.name}'
