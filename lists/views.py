from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery
from django.views.generic import ListView

from lists.mixins import WatchFavListViewMixin, PropMixin
from lists.models import Favourite

User = get_user_model()


class WatchlistListView(PropMixin, WatchFavListViewMixin, ListView):
    template_name = 'lists/watchlist.html'

    def get_queryset(self):
        return super().get_queryset().filter(watchlist__user=self.user).order_by('-watchlist__create_date')


class FavouriteListView(PropMixin, WatchFavListViewMixin, ListView):
    template_name = 'lists/favourite.html'

    def get_queryset(self):
        return super().get_queryset().filter(favourite__user=self.user).annotate(
            order=Subquery(Favourite.objects.filter(user=self.user, title=OuterRef('pk')).values('order')[:1]),
        ).order_by('favourite__order')
