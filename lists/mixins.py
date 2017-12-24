from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery, Exists

from lists.models import Watchlist, Favourite
from titles.models import Rating, Title

User = get_user_model()


class PropMixin:
    user = None
    is_owner = False

    def get_queryset(self):
        self.user = User.objects.get(username=self.kwargs['username'])
        self.is_owner = self.user.pk == self.request.user.pk
        return super().get_queryset()


class WatchFavListViewMixin:
    model = Title
    paginate_by = 0

    def get_queryset(self):
        self.user = User.objects.get(username=self.kwargs['username'])
        self.is_owner = self.user.pk == self.request.user.pk
        newest_ratings = Rating.objects.filter(user=self.user, title=OuterRef('pk')).order_by('-rate_date')

        qs = super().get_queryset().annotate(
            user_rate=Subquery(newest_ratings.values('rate')[:1]),
        )

        if self.request.user.is_authenticated:
            newest_request_user = Rating.objects.filter(
                user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')

            qs = qs.annotate(
                has_in_watchlist=Exists(
                    Watchlist.objects.filter(user=self.request.user, deleted=False, title=OuterRef('pk'))),
                has_in_favourites=Exists(Favourite.objects.filter(user=self.request.user, title=OuterRef('pk'))),
                request_user_rate=Subquery(newest_request_user.values('rate')[:1]),
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_owner': self.is_owner,
            'user': self.user
        })
        return context
