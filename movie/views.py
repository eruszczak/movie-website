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


def explore(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, 'Only logged in users can add to watchlist or favourites')
            return redirect(request.META.get('HTTP_REFERER'))

        title = get_object_or_404(Title, const=request.POST.get('const'))
        new_rating = request.POST.get('rating')
        # watch, unwatch = request.POST.get('watch'), request.POST.get('unwatch')
        # fav, unfav = request.POST.get('fav'), request.POST.get('unfav')

        if new_rating:
            create_or_update_rating(title, request.user, new_rating)
        # if watch or unwatch:
        #     toggle_title_in_watchlist(request.user, title, watch, unwatch)
        # if fav or unfav:
        #     toggle_title_in_favourites(request.user, title, fav, unfav)

        return redirect(request.META.get('HTTP_REFERER'))

    if request.user.is_authenticated:
        titles = Title.objects.annotate(
            has_in_watchlist=Count(
                Case(When(watchlist__user=request.user, watchlist__deleted=False, then=1), output_field=IntegerField())
            ),
            has_in_favourites=Count(
                Case(When(favourite__user=request.user, then=1), output_field=IntegerField())
            ),
        ).order_by('-year', '-votes')
    else:
        titles = Title.objects.all().order_by('-year', '-votes')

    search_result = []
    page = request.GET.get('page')

    selected_type = request.GET.get('t', '')
    query = request.GET.get('q')
    plot = request.GET.get('p')
    actor = request.GET.get('a')
    director = request.GET.get('d')
    genres = request.GET.getlist('g')
    username = request.GET.get('u')
    rating = request.GET.get('r')# if validate_rate(request.GET.get('r')) else None
    show_all_ratings = request.GET.get('all_ratings')
    rate_date_year = request.GET.get('year')
    rate_date_month = request.GET.get('month')
    year = request.GET.get('y')
    common = request.GET.get('common')
    exclude_his = request.GET.get('exclude_his')
    exclude_mine = request.GET.get('exclude_mine')

    if year:
        find_years = re.match(r'(\d{4})-*(\d{4})*', year)
        if find_years is not None:
            first_year, second_year = find_years.group(1), find_years.group(2)
            if first_year and second_year:
                if second_year < first_year:
                    first_year, second_year = second_year, first_year
                titles = titles.filter(year__lte=second_year, year__gte=first_year)
                search_result.append('Released between {} and {}'.format(first_year, second_year))
            elif first_year:
                titles = titles.filter(year=first_year)
                search_result.append('Released in {}'.format(first_year))

    if selected_type in ('movie', 'series'):
        titles = titles.filter(type__name=selected_type)
        search_result.append('Type: ' + selected_type)

    if query:
        titles = titles.filter(name__icontains=query) if len(query) > 2 else titles.filter(name__istartswith=query)
        search_result.append('Title {} "{}"'.format('contains' if len(query) > 2 else 'starts with', query))

    if plot:
        titles = titles.filter(plot__icontains=plot) if len(plot) > 2 else titles.filter(plot__istartswith=plot)
        search_result.append('Plot {} "{}"'.format('contains' if len(plot) > 2 else 'starts with', plot))

    if director:
        d = Director.objects.filter(id=director).first()
        if d is not None:
            titles = titles.filter(director=d)
            search_result.append('Directed by {}'.format(d.name))

    if actor:
        a = Actor.objects.filter(id=actor).first()
        if a is not None:
            titles = titles.filter(actor=a)
            search_result.append('With {}'.format(a.name))

    if genres:
        for genre in genres:
            titles = titles.filter(genre__name=genre)
        search_result.append('Genres: {}'.format(', '.join(genres)))

    want_req_user_rate = True

    req_user_id = request.user.id if request.user.is_authenticated() else 0
    searched_user = User.objects.filter(username=username).first()
    is_owner = request.user == searched_user
    if searched_user:
        if exclude_his and req_user_id:
            titles = titles.filter(rating__user=request.user).exclude(rating__user=searched_user)
            search_result.append('Seen by you and not by {}'.format(searched_user.username))
        elif exclude_mine and req_user_id and req_user_id != searched_user.id:
            want_req_user_rate = False

            titles = titles.filter(rating__user=searched_user).distinct().extra(select={
                'user_curr_rating': select_current_rating,
            }, select_params=[searched_user.id])
            titles = titles.exclude(rating__user=req_user_id)
            search_result.append('Seen by {} and not by me'.format(searched_user.username))
        elif common and req_user_id and not is_owner:
            titles = titles.filter(rating__user=searched_user).filter(rating__user=request.user).distinct().extra(select={
                'user_curr_rating': select_current_rating,
            }, select_params=[searched_user.id])
            search_result.append('Seen by you and {}'.format(searched_user.username))
        elif rating:
            titles = titles.filter(rating__user=searched_user).annotate(max_date=Max('rating__rate_date'))\
                .filter(rating__rate_date=F('max_date'), rating__rate=rating) \
                .extra(select={
                    'user_curr_rating': select_current_rating,
                }, select_params=[searched_user.id])
            search_result.append('Titles {} rated {}'.format(searched_user.username, rating))
        elif show_all_ratings:
            titles = Title.objects.filter(rating__user__username=searched_user.username) \
                .order_by('-rating__rate_date', '-rating__inserted_date')
            search_result.append('Seen by {}'.format(searched_user.username))
            search_result.append('Showing all ratings (duplicated titles)')
        elif not is_owner:
            titles = titles.filter(rating__user=searched_user).distinct().extra(select={
                'user_curr_rating': select_current_rating,
            }, select_params=[searched_user.id])
            search_result.append('Seen by {}'.format(searched_user.username))
        else:
            titles = titles.filter(rating__user=searched_user).order_by('-rating__rate_date')
            search_result.append('Seen by {}'.format(searched_user.username))
    elif rating and req_user_id:
        titles = titles.filter(rating__user=request.user)\
            .annotate(max_date=Max('rating__rate_date'))\
            .filter(rating__rate_date=F('max_date'), rating__rate=rating)
        search_result.append('Titles you rated {}'.format(rating))

    if rate_date_year and (username or req_user_id):
        if rate_date_year and rate_date_month:
            # here must be authenticated
            what_user_for = searched_user or request.user
            titles = titles.filter(rating__user=what_user_for, rating__rate_date__year=rate_date_year,
                                   rating__rate_date__month=rate_date_month)
            search_result.append('Seen in {} {}'.format(calendar.month_name[int(rate_date_month)], rate_date_year))
        elif rate_date_year:
            if username:
                titles = titles.filter(rating__user__username=username, rating__rate_date__year=rate_date_year)
            elif request.user.is_authenticated():
                titles = titles.filter(rating__user=request.user, rating__rate_date__year=rate_date_year)
            search_result.append('Seen in ' + rate_date_year)

    titles = titles.prefetch_related('director', 'genre')  # .distinct()
    if request.user.is_authenticated() and want_req_user_rate:
        titles = titles.extra(select={
            'req_user_curr_rating': select_current_rating,
        }, select_params=[request.user.id])

    ratings = paginate(titles, page, 25)

    # clean get parameters, but this only works in pagination links
    mutable_request_get = request.GET.copy()
    mutable_request_get.pop('page', None)
    empty_get_parameters = [k for k, v in mutable_request_get.items() if not v]
    for key in empty_get_parameters:
        del mutable_request_get[key]
    query_string = mutable_request_get.urlencode()

    context = {
        'page_title': 'Explore',
        'ratings': ratings,
        'searched_genres': genres,
        'search_result': search_result,
        'genres': Genre.objects.annotate(num=Count('title')).order_by('-num'),
        'followed_users': UserFollow.objects.filter(user_follower=request.user) if req_user_id else [],
        'query_string': '&{}'.format(query_string) if query_string else query_string,
    }
    # newest = Rating.objects.filter(user=request.user, title=OuterRef('pk')).order_by('-rate_date')
    # x = Title.objects.annotate(newest_user_rating=Subquery(newest.values('rate')[:1]))
    # print(x.first().newest_user_rating)
    return render(request, 'explore.html', context)


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
