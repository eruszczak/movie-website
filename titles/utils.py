from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import F, Q

from accounts.models import UserFollow
from recommend.models import Recommendation
from titles.models import Rating, CurrentlyWatchingTV
from lists.models import Watchlist, Favourite

User = get_user_model()


def toggle_watchlist(user=None, title=None, watch=None):
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


def toggle_favourite(user, title, fav=True):
    """deletes or adds title to user's favourites"""
    try:
        Favourite.objects.get(user=user, title=title).delete()
        return 'Removed from favourites'
    except Favourite.DoesNotExist:
        Favourite.objects.create(user=user, title=title)
        return 'Added to favourites'


def toggle_userfollow(follower, followed, add=True):
    try:
        UserFollow.objects.get(follower=follower, followed=followed).delete()
        return f'Unfollowed {followed.username}'
    except UserFollow.DoesNotExist:
        UserFollow.objects.create(follower=follower, followed=followed)
        return f'Followed {followed.username}'


def toggle_currentlywatchingtv(title, user, add=True):
    try:
        CurrentlyWatchingTV.objects.get(title=title, user=user).delete()
        return f'Not watching {title.name}'
    except CurrentlyWatchingTV.DoesNotExist:
        CurrentlyWatchingTV.objects.create(title=title, user=user)
        return f'Watching {title.name}'


# def recommend_title(title, sender, user_ids):
#     """sender recommends the title to user_ids"""
#     pks_of_followed_users = UserFollow.objects.filter(follower=sender).exclude(
#         Q(followed__rating__title=title) | Q(followed__recommendation__title=title)
#     ).values_list('followed__pk', flat=True)
#
#     users = User.objects.filter(Q(pk__in=pks_of_followed_users) & Q(pk__in=user_ids))
#     for user in users:
#         Recommendation.objects.create(user=user, sender=sender, title=title)
#
#     if users:
#         return f'Recommended to {users.count()} users'
#
#     return 'Already recommended'
