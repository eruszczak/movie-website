from django.db.models import OuterRef, Count, Case, When, IntegerField, Subquery
from django.views.generic import ListView

from lists.models import Favourite
from titles.models import Title, Rating
from titles.views import User


class WatchlistListView(ListView):
    template_name = 'lists/watchlist.html'
    model = Title
    paginate_by = 25
    user = None
    is_owner = False

    def get_queryset(self):
        self.user = User.objects.get(username=self.kwargs['username'])
        self.is_owner = self.user.pk == self.request.user.pk
        qs = super().get_queryset().filter(watchlist__user=self.user)
        newest_user = Rating.objects.filter(user=self.user, title=OuterRef('pk')).order_by('-rate_date')
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                has_in_watchlist=Count(
                    Case(
                        When(watchlist__user=self.request.user, watchlist__deleted=False, then=1),
                        output_field=IntegerField()
                    )
                ),
                has_in_favourites=Count(
                    Case(When(favourite__user=self.request.user, then=1), output_field=IntegerField())
                )
            )
            if self.is_owner:
                qs = qs.annotate(request_user_rate=Subquery(newest_user.values('rate')[:1]))
            else:
                newest_request_user = Rating.objects.filter(
                    user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')
                qs = qs.annotate(
                    user_rate=Subquery(newest_user.values('rate')[:1]),
                    request_user_rate=Subquery(newest_request_user.values('rate')[:1]),
                )
        else:
            qs = qs.annotate(user_rate=Subquery(newest_user.values('rate')[:1]))

        return qs.prefetch_related('genre', 'director')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            # 'count': {
            #     'deleted': get_deleted.count(),
            #     'archived': get_archived.count(),
            #     'active': get_active.count()
            # },
            'is_owner': self.is_owner,
            'user': self.user
        })
        return context


class FavouriteListView(ListView):
    template_name = 'lists/favourite.html'
    model = Title
    paginate_by = 0
    user = None
    is_owner = False

    def get_queryset(self):
        self.user = User.objects.get(username=self.kwargs['username'])
        self.is_owner = self.user.pk == self.request.user.pk
        newest_ratings = Rating.objects.filter(user=self.user, title=OuterRef('pk')).order_by('-rate_date')

        qs = super().get_queryset().filter(favourite__user=self.user).annotate(
            order=Subquery(Favourite.objects.filter(user=self.user, title=OuterRef('pk')).values('order')[:1]),
            user_rate=Subquery(newest_ratings.values('rate')[:1]),
        )

        if self.request.user.is_authenticated:
            newest_request_user = Rating.objects.filter(
                user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')

            qs = qs.annotate(
                has_in_watchlist=Count(
                    Case(
                        When(watchlist__user=self.request.user, watchlist__deleted=False, then=1),
                        output_field=IntegerField()
                    )
                ),
                has_in_favourites=Count(
                    Case(When(favourite__user=self.request.user, then=1), output_field=IntegerField())
                ),
                request_user_rate=Subquery(newest_request_user.values('rate')[:1]),
            )

        return qs.prefetch_related('genres').order_by('favourite__order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_owner': self.is_owner,
            'user': self.user
        })
        return context
