from django.contrib.auth import get_user_model

from accounts.models import UserFollow
from titles.models import CurrentlyWatchingTV
from lists.models import Watchlist, Favourite

User = get_user_model()


def toggle_watchlist(user, title):
    """adds or deletes title from user's watchlist"""
    try:
        Watchlist.objects.get(user=user, title=title).delete()
        return False, 'Removed from watchlist'
    except Watchlist.DoesNotExist:
        Watchlist.objects.create(user=user, title=title)
        return True, 'Added to watchlist'


def toggle_favourite(user, title):
    """deletes or adds title to user's favourites"""
    try:
        Favourite.objects.get(user=user, title=title).delete()
        return False, 'Removed from favourites'
    except Favourite.DoesNotExist:
        Favourite.objects.create(user=user, title=title)
        return True, 'Added to favourites'


def toggle_userfollow(follower, followed):
    """follows or unfollows user"""
    try:
        UserFollow.objects.get(follower=follower, followed=followed).delete()
        return False, f'Unfollowed {followed.username}'
    except UserFollow.DoesNotExist:
        UserFollow.objects.create(follower=follower, followed=followed)
        return True, f'Followed {followed.username}'


def toggle_currentlywatchingtv(title, user):
    """sets or unsets tv as currently watching"""
    try:
        CurrentlyWatchingTV.objects.get(title=title, user=user).delete()
        return False, f'Not watching {title.name}'
    except CurrentlyWatchingTV.DoesNotExist:
        CurrentlyWatchingTV.objects.create(title=title, user=user)
        return True, f'Watching {title.name}'
