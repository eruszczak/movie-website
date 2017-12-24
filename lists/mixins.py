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
        qs = super().get_queryset()\
            .annotate_rates(self.user, self.request.user)\
            .annotate_fav_and_watch(self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_owner': self.is_owner,
            'user': self.user
        })
        return context
