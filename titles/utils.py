from django.contrib.auth import get_user_model
from django.utils.timezone import now

from accounts.models import UserFollow
from titles.forms import RateForm
from titles.models import CurrentlyWatchingTV, Rating
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


def update_create_latest_rating(user, title, data):
    """if user already has rated a title - update it's rating else create new one (with today's date)"""
    try:
        instance = Rating.objects.filter(user=user, title=title).latest('rate_date')
    except Rating.DoesNotExist:
        data['rate_date'] = now().date()
        form = RateForm(user=user, title=title, data=data)
        message = 'Created rating'
    else:
        # instance already has rate_date but this field is required (also, do not need to pass title, user here)
        data['rate_date'] = instance.rate_date
        form = RateForm(data=data, instance=instance)
        message = 'Updated latest rating'
    return form, message


def update_rating_rate_or_create(user, rating_pk, data):
    """update rate of existing rating"""
    try:
        instance = Rating.objects.get(pk=rating_pk, user=user)
    except Rating.DoesNotExist:
        return None, 'Rating does not exist'
    else:
        data['rate_date'] = instance.rate_date
        form = RateForm(data=data, instance=instance)
        return form, f'Updated rating from {instance.rate_date}'
