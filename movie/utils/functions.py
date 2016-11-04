from django.db.models import F, Avg
from movie.models import Watchlist, Favourite, Rating
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def alter_title_in_watchlist(user, title, watchlist_instance, watch=None, unwatch=None):
    if watch:
        if watchlist_instance and watchlist_instance.deleted:
            # this is when you delete title imdb=True and then you add it again
            watchlist_instance.deleted = False
            watchlist_instance.save(update_fields=['deleted'])
        else:
            Watchlist.objects.create(user=user, title=title)
    elif unwatch:
        if watchlist_instance.imdb:
            watchlist_instance.deleted = True
            watchlist_instance.save(update_fields=['deleted'])
        else:
            watchlist_instance.delete()


def alter_title_in_favourites(user, title, fav=None, unfav=None):
    user_favourites = Favourite.objects.filter(user=user)
    if fav:
        Favourite.objects.create(user=user, title=title, order=user_favourites.count() + 1)
    elif unfav:
        favourite_instance = user_favourites.filter(title=title).first()
        user_favourites.filter(order__gt=favourite_instance.order).update(order=F('order') - 1)
        favourite_instance.delete()


def average_rating_of_title(title):
    # avg_all_ratings = title.rating_set.values('rate').aggregate(avg=Avg('rate'))
    sum_rate = 0
    ids_of_users = title.rating_set.values_list('user', flat=True).order_by('user').distinct()
    title_ratings = Rating.objects.filter(title=title)
    for user_id in ids_of_users:
        latest_rating = title_ratings.filter(user__id=user_id).first()
        sum_rate += latest_rating.rate
    if sum_rate:
        avg_rate = round(sum_rate / len(ids_of_users), 1)
        return '{} ({} users)'.format(avg_rate, len(ids_of_users))
    return None


def paginate(query_set, page, page_size=50):
    paginator = Paginator(query_set, page_size)
    try:
        ratings = paginator.page(page)
    except PageNotAnInteger:
        ratings = paginator.page(1)
    except EmptyPage:
        ratings = paginator.page(paginator.num_pages)
    return ratings
