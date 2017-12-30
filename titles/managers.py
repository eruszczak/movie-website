from django.db.models import Exists, Subquery, OuterRef
from django.db.models.query import QuerySet
from django.utils.timezone import now

from titles.constants import MOVIE, SERIES


class TitleQuerySet(QuerySet):

    def movies(self):
        return self.filter(type=MOVIE)

    def series(self):
        return self.filter(type=SERIES)

    def upcoming(self):
        return self.filter(release_date__gte=now().date())

    def annotate_fav_and_watch(self, request_user):
        from lists.models import Watchlist, Favourite

        if request_user.is_authenticated:
            return self.annotate(
                has_in_watchlist=Exists(
                    Watchlist.objects.filter(user=request_user, deleted=False, title=OuterRef('pk'))),
                has_in_favourites=Exists(Favourite.objects.filter(user=request_user, title=OuterRef('pk'))),
            )
        return self

    def annotate_rates(self, user=None, request_user=None):
        """annotates for each title latest rating for passed users"""
        from titles.models import Rating

        annotation = {}
        if user:
            annotation['user_rate'] = Subquery(
                Rating.objects.filter(
                    user=user, title=OuterRef('pk')
                ).order_by('-rate_date').values('rate')[:1]
            )
        if request_user and request_user.is_authenticated:
            annotation['request_user_rate'] = Subquery(
                Rating.objects.filter(
                    user=request_user, title=OuterRef('pk')
                ).order_by('-rate_date').values('rate')[:1]
            )

        if annotation:
            return self.annotate(**annotation)
        return self


class RatingQuerySet(QuerySet):

    def annotate_fav_and_watch(self, request_user):
        from lists.models import Watchlist, Favourite

        if request_user.is_authenticated:
            return self.annotate(
                has_in_watchlist=Exists(
                    Watchlist.objects.filter(user=request_user, deleted=False, title=OuterRef('title__pk'))),
                has_in_favourites=Exists(Favourite.objects.filter(user=request_user, title=OuterRef('title__pk'))),
            )
        return self

    def annotate_rates(self, request_user=None):
        """annotates for each title latest rating for passed users"""
        from titles.models import Rating

        if request_user and request_user.is_authenticated:
            return self.annotate(request_user_rate=Subquery(
                Rating.objects.filter(
                    user=request_user, title=OuterRef('title__pk')
                ).order_by('-rate_date').values('rate')[:1]
            ))
        return self
