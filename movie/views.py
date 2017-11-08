import re
import calendar
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count, Max, F, When, Case, IntegerField, Subquery
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.db.models import OuterRef

from common.prepareDB import update_title
from common.prepareDB_utils import validate_rate, convert_to_datetime
from common.sql_queries import curr_title_rating_of_followed, select_current_rating
from common.utils import paginate
from movie.functions import toggle_title_in_watchlist, toggle_title_in_favourites, recommend_title, create_or_update_rating
from users.models import UserFollow
from .models import Genre, Director, Title, Rating, Watchlist, Favourite, Actor


def home(request):
    if request.user.is_authenticated():
        user_ratings = Rating.objects.filter(user=request.user)

        context = {
            'ratings': user_ratings.select_related('title')[:16],

            'last_movie': user_ratings.filter(title__type__name='movie').select_related('title').first(),
            'last_series': user_ratings.filter(title__type__name='series').select_related('title').first(),
            'last_good_movie': user_ratings.filter(title__type__name='movie', rate__gte=9).select_related('title').first(),

            'movies_my_count': request.user.userprofile.count_movies,
            'series_my_count': request.user.userprofile.count_series,

            'rated_titles': request.user.userprofile.count_titles,
            'total_ratings': request.user.userprofile.count_ratings,

            'total_movies': reverse('explore') + '?t=movie', 'total_series': reverse('explore') + '?t=series',
            'search_movies': reverse('explore') + '?u={}&t=movie'.format(request.user.username),
            'search_series': reverse('explore') + '?u={}&t=series'.format(request.user.username)
        }
    else:
        context = {
            'ratings': Title.objects.all().order_by('-votes')[:16],
            'total_movies': reverse('explore') + '?t=movie',
            'total_series': reverse('explore') + '?t=series',

        }

    common_context = {
        'title': 'home',
        'movie_count': Title.objects.filter(type__name='movie').count(),
        'series_count': Title.objects.filter(type__name='series').count(),
    }

    context.update(common_context)
    return render(request, 'home.html', context)


def explore(request):
    if request.method == 'POST':
        if not request.user.is_authenticated():
            messages.info(request, 'Only logged in users can add to watchlist or favourites')
            return redirect(request.META.get('HTTP_REFERER'))

        title = get_object_or_404(Title, const=request.POST.get('const'))
        new_rating = request.POST.get('rating')
        watch, unwatch = request.POST.get('watch'), request.POST.get('unwatch')
        fav, unfav = request.POST.get('fav'), request.POST.get('unfav')

        if new_rating:
            create_or_update_rating(title, request.user, new_rating)
        if watch or unwatch:
            toggle_title_in_watchlist(request.user, title, watch, unwatch)
        if fav or unfav:
            toggle_title_in_favourites(request.user, title, fav, unfav)

        return redirect(request.META.get('HTTP_REFERER'))

    if request.user.is_authenticated():
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
    rating = request.GET.get('r') if validate_rate(request.GET.get('r')) else None
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


def title_details(request, slug):
    title = Title.objects.filter(slug=slug).first()
    if not title:
        title = Title.objects.get(const=slug)

    if request.method == 'POST':
        if not request.user.is_authenticated():
            messages.info(request, 'Only authenticated users can do this')
            return redirect(title)

        if request.POST.get('update_title'):
            is_updated, message = update_title(title)
            if is_updated:
                messages.success(request, message)
            else:
                messages.warning(request, message)

        selected_users = request.POST.getlist('choose_followed_user')
        if selected_users:
            message = recommend_title(title, request.user, selected_users)
            if message:
                messages.info(request, message, extra_tags='safe')

        new_rating, insert_as_new = request.POST.get('rating'), request.POST.get('insert_as_new')
        if new_rating:
            create_or_update_rating(title, request.user, new_rating, insert_as_new)

        delete_rating = request.POST.get('delete_rating')
        if delete_rating:
            to_delete = Rating.objects.filter(pk=request.POST.get('rating_pk'), user=request.user).first()
            if to_delete:
                in_watchlist = Watchlist.objects.filter(user=request.user, title=title,
                                                        added_date__date__lte=to_delete.rate_date, deleted=True).first()
                if in_watchlist:
                    toggle_title_in_watchlist(watch=True, instance=in_watchlist)
                to_delete.delete()
        return redirect(title)

    req_user_data = {}
    if request.user.is_authenticated():
        req_user_data = {
            'user_ratings_of_title': Rating.objects.filter(user=request.user, title=title),
            'is_favourite_for_user': Favourite.objects.filter(user=request.user, title=title).exists(),
            'is_in_user_watchlist': Watchlist.objects.filter(user=request.user, title=title, deleted=False).exists(),
            'followed_title_not_recommended': UserFollow.objects.filter(user_follower=request.user).exclude(
                user_followed__rating__title=title).exclude(user_followed__recommendation__title=title),
            'followed_saw_title': curr_title_rating_of_followed(request.user.id, title.id)
        }

    # todo caching or not a loop-way
    actors_and_other_titles = []
    for actor in title.actor.all():
        if request.user.is_authenticated:
            titles = Title.objects.filter(actor=actor).exclude(const=title.const).extra(select={
                'user_rate': """SELECT rate FROM movie_rating as rating
                WHERE rating.title_id = movie_title.id
                AND rating.user_id = %s
                ORDER BY rating.rate_date DESC LIMIT 1"""
            }, select_params=[request.user.id]).order_by('-votes')[:6]
        else:
            titles = Title.objects.filter(actor=actor).exclude(const=title.const).order_by('-votes')[:6]

        if titles:
            actors_and_other_titles.append((actor, titles))

    context = {
        'title': title,
        'data': req_user_data,
        'actors_and_other_titles': sorted(actors_and_other_titles, key=lambda x: len(x[1]))
    }
    return render(request, 'title_details.html', context)


class TitleDetailView(DetailView):
    query_pk_and_slug = False
    template_name = 'movie/title_detail.html'
    model = Title

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


def title_edit(request, slug):
    title = get_object_or_404(Title, slug=slug)
    current_rating = Rating.objects.filter(user__username=request.user.username, title=title).first()
    if not request.user.is_authenticated() or not current_rating:
        messages.info(request, 'You can edit titles you have rated, you must be logged in')
        return redirect(title)

    if request.method == 'POST':
        new_rate = request.POST.get('rate')
        new_date = convert_to_datetime(request.POST.get('newDateValue'), 'exported_from_db')

        if validate_rate(new_rate) and new_date:
            message = ''
            new_date = new_date.date()
            if new_date <= datetime.today().date() and not Rating.objects.filter(
                    user=request.user, title=title, rate_date=new_date).exists():
                if current_rating.rate != int(new_rate):
                    message += 'rating: {} changed for {}'.format(current_rating.rate, new_rate)
                    current_rating.rate = new_rate
                if current_rating.rate_date != new_date:
                    message += ', ' if message else ''
                    message += 'date: {} changed for {}'.format(current_rating.rate_date, new_date)
                    current_rating.rate_date = new_date
                if message:
                    messages.success(request, message)
                    current_rating.save(update_fields=['rate', 'rate_date'])
                else:
                    messages.info(request, 'Nothing changed')
            else:
                messages.warning(request, 'Future date or you already have a rating for this title with this date')
        else:
            messages.warning(request, 'Invalid values')

        return redirect(title)

    context = {
        'entry': current_rating,
    }
    return render(request, 'title_edit.html', context)


def groupby_year(request):
    context = {
        'year_count': Title.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
        'title_count': Title.objects.all().count()
    }
    return render(request, 'groupby_year.html', context)


def groupby_genre(request):
    context = {
        'genre': Genre.objects.annotate(num=Count('title')).order_by('-num'),
    }
    return render(request, 'groupby_genre.html', context)


def groupby_director(request):
    context = {
        'director': Director.objects.filter(title__type__name='movie').annotate(num=Count('title')).order_by('-num')[:50],
    }
    return render(request, 'groupby_director.html', context)


def watchlist(request, username):
    user = get_object_or_404(User, username=username)
    user_watchlist = Watchlist.objects.filter(user=user)
    is_owner = request.user == user
    page = request.GET.get('page')

    get_active = user_watchlist.filter(deleted=False)
    get_deleted = user_watchlist.filter(imdb=True, deleted=True)
    get_archived = user_watchlist.filter(title__rating__title=F('title'),
                                         title__rating__rate_date__gte=F('added_date')).distinct()
    if request.GET.get('show_deleted'):
        user_watchlist = get_deleted
        context = {
            'user_watchlist_deleted': user_watchlist,
            'query_string': '?show_deleted=true&page=',
        }
    elif request.GET.get('show_archived'):
        user_watchlist = get_archived
        context = {
            'user_watchlist_archived': user_watchlist,
            'query_string': '?show_archived=true&page=',
        }
    else:
        user_watchlist = get_active
        context = {'user_watchlist': user_watchlist}

    if request.user.is_authenticated():
        user_watchlist = user_watchlist.annotate(
            has_in_watchlist=Count(
                Case(When(user=request.user.id, deleted=False, then=1), output_field=IntegerField())
            ),
            has_in_favourites=Count(
                Case(When(title__favourite__user=request.user.id, then=1), output_field=IntegerField())
            )
        )
        if is_owner:
            user_watchlist = user_watchlist.extra(select={
                'req_user_curr_rating': select_current_rating,
            }, select_params=[request.user.id])
        else:
            user_watchlist = user_watchlist.extra(select={
                'req_user_curr_rating': """SELECT rate FROM movie_rating as rating
                    WHERE rating.title_id = movie_title.id
                    AND rating.user_id = %s
                    ORDER BY rating.rate_date DESC LIMIT 1""",
                'user_curr_rating': """SELECT rate FROM movie_rating as rating
                    WHERE rating.title_id = movie_title.id
                    AND rating.user_id = %s
                    ORDER BY rating.rate_date DESC LIMIT 1""",
            }, select_params=[request.user.id, user.id])
    else:
        user_watchlist = user_watchlist.extra(select={
            'user_curr_rating': select_current_rating,
        }, select_params=[user.id])

    user_watchlist = user_watchlist.select_related('title').prefetch_related('title__director', 'title__genre')
    objs = paginate(user_watchlist, page, 25)
    context.update({
        'objs': objs,
        'is_owner': is_owner,
        'username': username,
        'choosen_user': user,
        'title': username + '\'s watchlist',
        'count': {
            'deleted': get_deleted.count(),
            'archived': get_archived.count(),
            'active': get_active.count()
        }
    })
    return render(request, 'watchlist.html', context)


def favourite(request, username):
    user = get_object_or_404(User, username=username)
    user_favourites = Favourite.objects.filter(user=user)
    is_owner = request.user == user

    if request.method == 'POST':
        if not request.user == user:
            messages.info(request, 'You can change order only for your list')
            return redirect(user.userprofile.favourite_url())

        new_title_order = request.POST.get('item_order')
        if new_title_order:
            new_title_order = re.findall('tt\d{7}', new_title_order)
            for new_position, const in enumerate(new_title_order, 1):
                user_favourites.filter(title__const=const).update(order=new_position)

    if request.user.is_authenticated():
        faved_titles = Title.objects.filter(favourite__user=user).annotate(
            has_in_watchlist=Count(
                Case(When(watchlist__user=request.user, watchlist__deleted=False, then=1), output_field=IntegerField())
            ),
            has_in_favourites=Count(
                Case(When(favourite__user=request.user, then=1), output_field=IntegerField())
            )
        )
        if is_owner:
            faved_titles = faved_titles.extra(select={
                'req_user_curr_rating': select_current_rating
            }, select_params=[request.user.id]).prefetch_related('genre', 'director').order_by('favourite__order')
        else:
            faved_titles = faved_titles.extra(select={
                'req_user_curr_rating': """SELECT rate FROM movie_rating as rating
                    WHERE rating.title_id = movie_title.id
                    AND rating.user_id = %s
                    ORDER BY rating.rate_date DESC LIMIT 1""",
                'user_curr_rating': """SELECT rate FROM movie_rating as rating
                    WHERE rating.title_id = movie_title.id
                    AND rating.user_id = %s
                    ORDER BY rating.rate_date DESC LIMIT 1""",
            }, select_params=[request.user.id, user.id]).prefetch_related('genre', 'director').order_by('favourite__order')
    else:
        faved_titles = Title.objects.filter(favourite__user=user).extra(select={
            'user_curr_rating': select_current_rating
        }, select_params=[user.id]).prefetch_related('genre', 'director').order_by('favourite__order')

    # page = request.GET.get('page')
    # paginated_titles = paginate(faved_titles, page, 50)

    context = {
        'ratings': faved_titles[:100],
        'is_owner': is_owner,
        'title': username + '\'s favourites',
        'username': username,
        'choosen_user': user
    }
    return render(request, 'favourite.html', context)


def add_title(request):
    return render(request, '')

