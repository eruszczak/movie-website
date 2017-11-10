import re
import calendar
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count, Max, F, When, Case, IntegerField, Subquery
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView, RedirectView, ListView, UpdateView
from django.db.models import OuterRef

from common.prepareDB import update_title
from common.prepareDB_utils import convert_to_datetime
from common.sql_queries import curr_title_rating_of_followed, select_current_rating
from common.utils import paginate
from movie.forms import TitleSearchForm, RateUpdateForm
from movie.functions import toggle_title_in_watchlist, toggle_title_in_favourites, recommend_title, create_or_update_rating
from movie.shared import SearchViewMixin
from users.models import UserFollow
from .models import Genre, Director, Title, Rating, Watchlist, Favourite, Actor


class HomeView(TemplateView):
    template_name = 'movie/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'home',
            'movie_count': Title.objects.filter(type__name='movie').count(),
            'series_count': Title.objects.filter(type__name='series').count(),
        })
        if self.request.user.is_authenticated:
            user_ratings = Rating.objects.filter(user=self.request.user)
            context.update({
                'ratings': user_ratings.select_related('title')[:16],

                'last_movie': user_ratings.filter(title__type__name='movie').select_related('title').first(),
                'last_series': user_ratings.filter(title__type__name='series').select_related('title').first(),
                'last_good_movie': user_ratings.filter(title__type__name='movie', rate__gte=9).select_related(
                    'title').first(),
                'movies_my_count': self.request.user.userprofile.count_movies,
                'series_my_count': self.request.user.userprofile.count_series,

                'rated_titles': self.request.user.userprofile.count_titles,
                'total_ratings': self.request.user.userprofile.count_ratings,

                'total_movies': reverse('explore') + '?t=movie', 'total_series': reverse('explore') + '?t=series',
                'search_movies': reverse('explore') + '?u={}&t=movie'.format(self.request.user.username),
                'search_series': reverse('explore') + '?u={}&t=series'.format(self.request.user.username)
            })
        else:
            context.update({
                'ratings': Title.objects.all().order_by('-votes')[:16],
                'total_movies': reverse('explore') + '?t=movie',
                'total_series': reverse('explore') + '?t=series',

            })
        return context


# new_rating = request.POST.get('rating')
# if new_rating:
#     create_or_update_rating(title, request.user, new_rating)

class TitleListView(SearchViewMixin, ListView):
    search_form_class = TitleSearchForm
    template_name = 'movie/title_list.html'
    paginate_by = 25
    model = Title

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                has_in_watchlist=Count(
                    Case(When(watchlist__user=self.request.user, watchlist__deleted=False, then=1),
                         output_field=IntegerField())
                ),
                has_in_favourites=Count(
                    Case(When(favourite__user=self.request.user, then=1), output_field=IntegerField())
                ),
            )
        return qs.order_by('-year', '-votes').prefetch_related('director', 'genre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TitleDetailView(DetailView):
    query_pk_and_slug = False
    template_name = 'movie/title_detail.html'
    model = Title
    object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['data'] = {
                'user_ratings_of_title': Rating.objects.filter(user=self.request.user, title=self.object),
                'is_favourite_for_user': Favourite.objects.filter(user=self.request.user, title=self.object).exists(),
                'is_in_user_watchlist': Watchlist.objects.filter(user=self.request.user, title=self.object,
                                                                 deleted=False).exists(),
                'followed_title_not_recommended': UserFollow.objects.filter(user_follower=self.request.user).exclude(
                    user_followed__rating__title=self.object).exclude(user_followed__recommendation__title=self.object),
                'followed_saw_title': curr_title_rating_of_followed(self.request.user.id, self.object.pk)
            }

        actors_and_other_titles = []
        for actor in self.object.actor.all():
            if self.request.user.is_authenticated:
                newest = Rating.objects.filter(user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')
                titles = Title.objects.filter(actor=actor).exclude(const=self.object.const).annotate(
                    user_rate=Subquery(newest.values('rate')[:1])).order_by('-votes')[:6]
            else:
                titles = Title.objects.filter(actor=actor).exclude(const=self.object.const).order_by('-votes')[:6]

            if titles:
                actors_and_other_titles.append((actor, titles))

        context.update({
            'actors_and_other_titles': actors_and_other_titles
            # why sorted(actors_and_other_titles, key=lambda x: len(x[1]))
        })
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        # self.update_title()
        self.object = self.get_object()
        self.recommend_title_to_other_users()
        self.create_or_update_rating()
        self.delete_rating()
        # todo: use if (allow only one action per one post) and call messages only once
        return redirect(self.object)

    # def update_title(self):
    #     if self.request.POST.get('update_title'):
    #         is_updated, message = update_title(self.object)
    #         if is_updated:
    #             messages.success(self.request, message)
    #         else:
    #             messages.warning(self.request, message)

    def recommend_title_to_other_users(self):
        selected_users = self.request.POST.getlist('choose_followed_user')
        if selected_users:
            message = recommend_title(self.object, self.request.user, selected_users)
            if message:
                messages.info(self.request, message, extra_tags='safe')

    def create_or_update_rating(self):
        new_rating, insert_as_new = self.request.POST.get('rating'), self.request.POST.get('insert_as_new')
        if new_rating:
            create_or_update_rating(self.object, self.request.user, new_rating, insert_as_new)

    def delete_rating(self):
        delete_rating = self.request.POST.get('delete_rating')
        rating_pk = self.request.POST.get('rating_pk')
        if delete_rating and rating_pk:
            to_delete = Rating.objects.filter(pk=rating_pk, user=self.request.user).first()
            query = {
                    'user': self.request.user,
                    'title': self.object,
                    'added_date__date__lte': to_delete.rate_date,
                    'deleted': True
            }
            in_watchlist = Watchlist.objects.filter(**query).first()
            if in_watchlist:
                toggle_title_in_watchlist(watch=True, instance=in_watchlist)
            to_delete.delete()


class RatingUpdateView(UpdateView):
    model = Rating
    template_name = 'movie/rating_update.html'
    form_class = RateUpdateForm


class GroupByGenreView(TemplateView):
    template_name = 'movie/group_by_genre.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'genre': Genre.objects.annotate(num=Count('title')).order_by('-num')
        })
        return context


class GroupByDirectorView(TemplateView):
    template_name = 'movie/group_by_director.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'director': Director.objects.filter(
                title__type__name='movie').annotate(num=Count('title')).order_by('-num')[:50]
        })
        return context


class GroupByYearView(TemplateView):
    template_name = 'movie/group_by_year.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'year_count': Title.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
            'title_count': Title.objects.all().count()
        })
        return context


# get_active = user_watchlist.filter(deleted=False)
# get_deleted = user_watchlist.filter(imdb=True, deleted=True)
# get_archived = user_watchlist.filter(title__rating__title=F('title'), title__rating__rate_date__gte=F('added_date')).distinct()
class WatchlistListView(ListView):
    template_name = 'watchlist.html'
    model = Watchlist
    paginate_by = 25
    user = None
    is_owner = False

    # todo: search form
    def get_queryset(self):
        self.user = User.objects.get(username=self.kwargs['username'])
        self.is_owner = self.user.pk == self.request.user
        qs = super().get_queryset().filter(user=self.user)
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                has_in_watchlist=Count(
                    Case(When(user=self.request.user.id, deleted=False, then=1), output_field=IntegerField())
                ),
                has_in_favourites=Count(
                    Case(When(title__favourite__user=self.request.user.id, then=1), output_field=IntegerField())
                )
            )
            if self.is_owner:
                qs = qs.extra(select={
                    'req_user_curr_rating': select_current_rating,
                }, select_params=[self.request.user.id])
            else:
                # TODO
                qs = qs.extra(select={
                    'req_user_curr_rating': """SELECT rate FROM movie_rating as rating
                        WHERE rating.title_id = movie_title.id
                        AND rating.user_id = %s
                        ORDER BY rating.rate_date DESC LIMIT 1""",
                    'user_curr_rating': """SELECT rate FROM movie_rating as rating
                        WHERE rating.title_id = movie_title.id
                        AND rating.user_id = %s
                        ORDER BY rating.rate_date DESC LIMIT 1""",
                }, select_params=[self.request.user.id, self.user.id])
        else:
            # TODO
            qs = qs.extra(select={
                'user_curr_rating': select_current_rating,
            }, select_params=[self.user.id])

        return qs.select_related('title').prefetch_related('title__director', 'title__genre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            # 'count': {
            #     'deleted': get_deleted.count(),
            #     'archived': get_archived.count(),
            #     'active': get_active.count()
            # },
            'is_owner': False,
            'user': self.user
        })
        return context


# new_title_order = request.POST.get('item_order')
# if new_title_order:
#     new_title_order = re.findall('tt\d{7}', new_title_order)
#     for new_position, const in enumerate(new_title_order, 1):
#         user_favourites.filter(title__const=const).update(order=new_position)
class FavouriteListView(ListView):
    template_name = 'favourite.html'
    model = Title
    paginate_by = 25
    user = None
    is_owner = False

    def get_queryset(self):
        self.user = User.objects.get(username=self.kwargs['username'])
        self.is_owner = self.user.pk == self.request.user
        qs = super().get_queryset().filter(favourite__user=self.user)
        if self.request.user.is_authenticated:
            qs = qs.filter(favourite__user=self.user).annotate(
                has_in_watchlist=Count(
                    Case(When(watchlist__user=self.request.user, watchlist__deleted=False, then=1), output_field=IntegerField())
                ),
                has_in_favourites=Count(
                    Case(When(favourite__user=self.request.user, then=1), output_field=IntegerField())
                )
            )
            if self.is_owner:
                qs = qs.extra(select={
                    'req_user_curr_rating': select_current_rating
                }, select_params=[self.request.user.id])
            else:
                qs = qs.extra(select={
                    'req_user_curr_rating': """SELECT rate FROM movie_rating as rating
                        WHERE rating.title_id = movie_title.id
                        AND rating.user_id = %s
                        ORDER BY rating.rate_date DESC LIMIT 1""",
                    'user_curr_rating': """SELECT rate FROM movie_rating as rating
                        WHERE rating.title_id = movie_title.id
                        AND rating.user_id = %s
                        ORDER BY rating.rate_date DESC LIMIT 1""",
                }, select_params=[self.request.user.id, self.user.id])
        else:
            qs = qs.filter(favourite__user=self.user).extra(select={
                'user_curr_rating': select_current_rating
            }, select_params=[self.user.id])
        return qs.prefetch_related('genre', 'director').order_by('favourite__order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_owner': False,
            'user': self.user
        })
        return context


class TitleRedirectView(RedirectView):
    pattern_name = 'title-detail'

    def get_redirect_url(self, *args, **kwargs):
        title = get_object_or_404(Title, const=kwargs['const'])
        return title.get_absolute_url()
