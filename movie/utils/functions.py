from django.template.defaultfilters import slugify
from django.db.models import F
# models are imported within functions to prevent circular dependencies


def alter_title_in_watchlist(user, title, watch=None, unwatch=None):
    from ..models import Watchlist
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


def alter_title_in_favourites(user, title, fav=None, unfav=None):
    from ..models import Favourite
    user_favourites = Favourite.objects.filter(user=user)
    if fav is not None:
        Favourite.objects.create(user=user, title=title, order=user_favourites.count() + 1)
    elif unfav is not None:
        favourite_instance = user_favourites.filter(title=title).first()
        user_favourites.filter(order__gt=favourite_instance.order).update(order=F('order') - 1)
        favourite_instance.delete()


def create_slug(title, new_slug=None):
    from ..models import Title
    # recursive function to get unique slug (in case of 2 titles with the same name/year)
    slug = slugify('{} {}'.format(title.name, title.year))[:70] if new_slug is None else new_slug
    if Title.objects.filter(slug=slug).exists():
        slug += 'i'
        create_slug(title, slug)
    return slug

