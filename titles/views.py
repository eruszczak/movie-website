from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Count, When, Case, IntegerField, Subquery, Q
from django.db.models import OuterRef
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView, RedirectView, ListView, UpdateView

from accounts.models import UserFollow
from lists.models import Watchlist, Favourite
from recommend.forms import RecommendTitleForm
from shared.views import SearchViewMixin
from titles.forms import TitleSearchForm, RateUpdateForm
from .models import Genre, Director, Title, Rating

User = get_user_model()


class HomeView(TemplateView):
    template_name = 'titles/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'movie_count': Title.objects.filter(type__name='title').count(),
            'series_count': Title.objects.filter(type__name='series').count(),
        })
        if self.request.user.is_authenticated:
            user_ratings = Rating.objects.filter(user=self.request.user)
            # newest = Rating.objects.filter(user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')
            qs = user_ratings.annotate(
                has_in_watchlist=Count(
                    Case(
                        When(title__watchlist__user=self.request.user, title__watchlist__deleted=False, then=1),
                        output_field=IntegerField()
                    )
                ),
                has_in_favourites=Count(
                    Case(When(title__favourite__user=self.request.user, then=1), output_field=IntegerField())
                ),
            )
            context.update({
                'rating_list': qs[:6],
                'ratings': user_ratings.select_related('title')[:16],

                'last_movie': user_ratings.filter(title__type__name='title').select_related('title').first(),
                'last_series': user_ratings.filter(title__type__name='series').select_related('title').first(),
                'last_good_movie': user_ratings.filter(title__type__name='title', rate__gte=9).select_related(
                    'title').first(),
                'movies_my_count': self.request.user.count_movies,
                'series_my_count': self.request.user.count_series,

                'rated_titles': self.request.user.count_titles,
                'total_ratings': self.request.user.count_ratings,

                # 'total_movies': reverse('title-list') + '?t=title',
                # 'total_series': reverse('title-list') + '?t=series',
                # 'search_movies': reverse('title-list') + '?u={}&t=title'.format(self.request.user.username),
                # 'search_series': reverse('title-list') + '?u={}&t=series'.format(self.request.user.username)
            })
        else:
            context.update({
                'ratings': Title.objects.all().order_by('-votes')[:16],
                'total_movies': reverse('title-list') + '?t=title',
                'total_series': reverse('title-list') + '?t=series',

            })
        return context


class TitleListView(SearchViewMixin, ListView):
    search_form_class = TitleSearchForm
    template_name = 'titles/title_list.html'
    paginate_by = 20
    model = Title

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            newest = Rating.objects.filter(user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')
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
                user_rate=Subquery(newest.values('rate')[:1])
            )
        return qs.order_by('-year', '-name').prefetch_related('genre')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context


class TitleDetailView(DetailView):
    query_pk_and_slug = False
    template_name = 'titles/title_detail.html'
    model = Title
    object = None
    # recommend_form_class = RecommendTitleForm

    # def get_queryset(self):
    #     return super().get_queryset().prefetch_related('genre', 'actor', 'director')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                has_in_favourites=Count(
                    Case(When(favourite__user=self.request.user, then=1), output_field=IntegerField())
                ),
                has_in_watchlist=Count(
                    Case(
                        When(watchlist__user=self.request.user, watchlist__deleted=False, then=1),
                        output_field=IntegerField()
                    )
                ),
            )
        try:
            return queryset.get(const=self.kwargs['const'])
        except self.model.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context.update({
                # 'rating': Rating.objects.filter(user=self.request.user, title=self.object).latest('rate_date'),
                'user_ratings_of_title': Rating.objects.filter(user=self.request.user, title=self.object),
                'is_favourite_for_user': Favourite.objects.filter(user=self.request.user, title=self.object).exists(),
                'is_in_user_watchlist': Watchlist.objects.filter(
                    user=self.request.user, title=self.object, deleted=False).exists(),
                'followed_title_not_recommended': UserFollow.objects.filter(follower=self.request.user).exclude(
                    Q(followed__rating__title=self.object) | Q(followed__recommendation__title=self.object)
                ).select_related('followed'),
                # 'recommend_form': self.recommend_form_class(self.request.user, self.object),
                'followed_saw_title': UserFollow.objects.filter(
                    follower=self.request.user, followed__rating__title=self.object).annotate(
                    user_rate=Subquery(
                        Rating.objects.filter(
                            user=OuterRef('followed'), title=OuterRef('followed__rating__title')
                        ).order_by('-rate_date').values('rate')[:1]
                    ),
                    user_rate_date=Subquery(
                        Rating.objects.filter(
                            user=OuterRef('followed'), title=OuterRef('followed__rating__title')
                        ).order_by('-rate_date').values('rate_date')[:1]
                    )
                ).select_related('followed')
            })

        actors_and_other_titles = []
        # newest = Rating.objects.filter(user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')
        # test = Title.objects.filter(actor__in=self.object.actor.all())
        # print(test)
        for actor in self.object.actor.all():
            if self.request.user.is_authenticated:
                newest = Rating.objects.filter(user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')
                titles = Title.objects.filter(actor=actor).exclude(const=self.object.const).annotate(
                    user_rate=Subquery(newest.values('rate')[:1])).order_by('-votes')
            else:
                titles = Title.objects.filter(actor=actor).exclude(const=self.object.const).order_by('-votes')

            if titles:
                actors_and_other_titles.append((actor, titles))

        context.update({
            'actors_and_other_titles': sorted(actors_and_other_titles, key=lambda x: len(x[1]))
        })
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # self.delete_rating()
        return redirect(self.object)

    # def delete_rating(self):
    #     delete_rating = self.request.POST.get('delete_rating')
    #     rating_pk = self.request.POST.get('rating_pk')
    #     if delete_rating and rating_pk:
    #         to_delete = Rating.objects.filter(pk=rating_pk, user=self.request.user).first()
    #         query = {
    #                 'user': self.request.user,
    #                 'title': self.object,
    #                 'added_date__date__lte': to_delete.rate_date,
    #                 'deleted': True
    #         }
    #         in_watchlist = Watchlist.objects.filter(**query).first()
    #         if in_watchlist:
    #             toggle_title_in_watchlist(watch=True, instance=in_watchlist)
    #         to_delete.delete()


class RatingUpdateView(UpdateView):
    model = Rating
    template_name = 'titles/rating_update.html'
    form_class = RateUpdateForm


class GroupByGenreView(TemplateView):
    template_name = 'titles/group_by_genre.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'genre': Genre.objects.annotate(num=Count('title')).order_by('-num')
        })
        return context


class GroupByDirectorView(TemplateView):
    template_name = 'titles/group_by_director.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'director': Director.objects.filter(
                title__type__name='title').annotate(num=Count('title')).order_by('-num')[:50]
        })
        return context


class GroupByYearView(TemplateView):
    template_name = 'titles/group_by_year.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'year_count': Title.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
            'title_count': Title.objects.all().count()
        })
        return context


class TitleRedirectView(RedirectView):
    pattern_name = 'title-detail'

    def get_redirect_url(self, *args, **kwargs):
        title = get_object_or_404(Title, const=kwargs['const'])
        return title.get_absolute_url()
