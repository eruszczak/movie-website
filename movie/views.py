import re
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .forms import EditRating
from .models import Genre, Director, Title, Rating, Watchlist, Favourite
from users.models import UserFollow
from recommend.models import Recommendation
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q, When, Case, IntegerField
from datetime import datetime
from .utils.functions import alter_title_in_watchlist, alter_title_in_favourites, paginate, average_rating_of_title
from django.http import Http404


def home(request):
    all_movies = Rating.objects.filter(title__type__name='movie').order_by('-rate_date')
    all_series = Rating.objects.filter(title__type__name='series').order_by('-rate_date')
    movie_titles = Title.objects.filter(type__name='movie')
    series_titles = Title.objects.filter(type__name='series')
    if request.user.is_authenticated():
        all_movies = all_movies.filter(user=request.user)
        all_series = all_series.filter(user=request.user)
    context = {
        'ratings': all_movies[:16],
        'last_movie': all_movies.first().title if all_movies else None,
        'last_series': all_series.first().title if all_series else None,
        'last_good_movie': all_movies.filter(rate__gte=9).first().title if all_movies.filter(rate__gte=9) else None,
        'movie_count': movie_titles.count(),
        'series_count': series_titles.count(),
        'movies_my_count': all_movies.values('title').distinct().count(),
        'series_my_count': all_series.values('title').distinct().count(),
        'total_movies': reverse('explore') + '?t=movie',
        'total_series': reverse('explore') + '?t=series',
    }
    # can refactor += this but when template will be done. atm its not worth it bcs i use separate names for keys
    if request.user.is_authenticated():
        context['search_movies'] = reverse('explore') + '?u={}&t=movie'.format(request.user.username)
        context['search_series'] = reverse('explore') + '?u={}&t=series'.format(request.user.username)
    else:
        context['total_movies'] = reverse('explore') + '?t=movie'
        context['total_series'] = reverse('explore') + '?t=series'
    return render(request, 'home.html', context)


def explore(request):
    if request.method == 'POST':
        requested_obj = get_object_or_404(Title, const=request.POST.get('const'))
        if not request.user.is_authenticated():
            messages.info(request, 'Only logged in users can add to watchlist or favourites')
            return redirect(request.META.get('HTTP_REFERER'))

        watch, unwatch = request.POST.get('watch'), request.POST.get('unwatch')
        if watch or unwatch:
            obj_in_watchlist = Watchlist.objects.filter(user=request.user, title=requested_obj).first()
            alter_title_in_watchlist(request.user, requested_obj, obj_in_watchlist, watch, unwatch)

        fav, unfav = request.POST.get('fav'), request.POST.get('unfav')
        if fav or unfav:
            alter_title_in_favourites(request.user, requested_obj, fav, unfav)
        return redirect(request.META.get('HTTP_REFERER'))

    if request.user.is_authenticated():
        titles = Title.objects.annotate(
            seen_by_user=Count(
                Case(When(rating__user=request.user, then=1), output_field=IntegerField())
            ),
            has_in_watchlist=Count(
                Case(When(watchlist__user=request.user, watchlist__deleted=False, then=1), output_field=IntegerField())
            ),
            has_in_favourites=Count(
                Case(When(favourite__user=request.user, then=1), output_field=IntegerField())
            ),
        ).order_by('-year', '-votes')
    else:
        titles = Title.objects.all().order_by('-year', '-votes')
    query_string = ''   # this is needed for pagination buttons while searching

    year = request.GET.get('y')
    if year:
        find_years = re.match(r'(\d{4})-*(\d{4})*', year)
        first_year, second_year = find_years.group(1), find_years.group(2)
        if first_year and second_year:
            titles = titles.filter(year__lte=second_year, year__gte=first_year)
        elif first_year:
            titles = titles.filter(year=first_year)
            query_string += '{}={}&'.format('y', year)

    selected_type = request.GET.get('t', '')
    if selected_type in ('movie', 'series'):
        titles = titles.filter(Q(type__name=selected_type))
        query_string += '{}={}&'.format('t', selected_type)

    query = request.GET.get('q')
    if query:
        titles = titles.filter(name__icontains=query) if len(query) > 2 else titles.filter(name__startswith=query)
        query_string += '{}={}&'.format('q', query)

    director = request.GET.get('d')
    if director:
        titles = titles.filter(director__id=director)
        query_string += '{}={}&'.format('d', director)

    genres = request.GET.getlist('g')
    if genres:
        for genre in genres:
            titles = titles.filter(genre__name=genre)
            query_string += '{}={}&'.format('g', genre)

    user = request.GET.get('u')
    if user is not None:
        query_string += '{}={}&'.format('u', user)
        if request.GET.get('exclude_his'):
            titles = titles.exclude(rating__user__username=user)
            query_string += 'exclude_his=on&'
        elif request.GET.get('exclude_mine'):
            titles = titles.filter(rating__user__username=user).exclude(rating__user=request.user)
            query_string += 'exclude_mine=on&'
        else:
            titles = titles.filter(rating__user__username=user)
            rating = request.GET.get('r')
            if rating:
                titles = titles.filter(rating__rate=rating)
                query_string += '{}={}&'.format('r', rating)
    else:
        rating = request.GET.get('r')
        if rating and request.user.is_authenticated():
            titles = titles.filter(rating__user=request.user, rating__rate=rating)
            query_string += '{}={}&'.format('r', rating)

    # only if you specified ?u= or you are logged in
    rate_date_year, rate_date_month = request.GET.get('year'), request.GET.get('month')
    if rate_date_year and (user or request.user.is_authenticated()):
        # if user: ratings are already filtered for him
        if not user:
            titles = titles.filter(rating__user=request.user)
        if rate_date_year and rate_date_month:
            titles = titles.filter(rating__rate_date__year=rate_date_year, rating__rate_date__month=rate_date_month)
            query_string += '{}={}&'.format('year', rate_date_year)
            query_string += '{}={}&'.format('month', rate_date_month)
        elif rate_date_year:
            titles = titles.filter(rating__rate_date__year=rate_date_year)
            query_string += '{}={}&'.format('year', rate_date_year)

    page = request.GET.get('page')
    titles = titles.distinct()
    ratings = paginate(titles, page)

    if query_string:
        query_string = '?' + query_string + 'page='

    context = {
        'ratings': ratings,
        'query': query,
        'selected_type': selected_type,
        'genres': Genre.objects.annotate(num=Count('title')).order_by('-num'),
        # 'users': User.objects.annotate(num=Count('title')).order_by('-num'),
        'list_of_users': User.objects.all() if not request.user.is_authenticated() else User.objects.exclude(pk=request.user.pk),
        'query_string': query_string,
    }
    return render(request, 'explore.html', context)


def title_details(request, slug):
    title = Title.objects.filter(slug=slug).first()
    if not title:
        # if no title -> check if this is imdb const
        title = Title.objects.filter(const=slug).first()
        if not title:
            raise Http404
    if request.user.is_authenticated():
        user_ratings_of_title = Rating.objects.filter(user=request.user, title=title)
        current_rating = user_ratings_of_title.first()
        is_favourite_for_user = Favourite.objects.filter(user=request.user, title=title).exists()
        is_in_user_watchlist = Watchlist.objects.filter(user=request.user, title=title, deleted=False).exists()
        # followed = [obj.user_followed for obj in UserFollow.objects.filter(user_follower=request.user)
        #             if not Recommendation.objects.filter(user=obj.user_followed, title=title).exists()
        #             and not Rating.objects.filter(user=obj.user_followed, title=title).exists()]
        followed = UserFollow.objects.filter(user_follower=request.user).extra(select={
            'latest_rate': """
                SELECT rate from movie_rating as rating, movie_title as title
                WHERE rating.title_id = title.id
                AND rating.user_id = users_userfollow.user_followed_id
                AND title.id = %s
                ORDER BY rating.rate_date DESC LIMIT 1""",
            'has_in_recommend': """
                SELECT 1 from recommend_recommendation as recommend, movie_title as title
                WHERE recommend.title_id = title.id
                AND recommend.user_id = users_userfollow.user_followed_id
                AND title.id = %s""",
        }, select_params=[title.id] * 2)
        # for checking if recommended can use CASE
        followed_can_take_recommendation = [obj.user_followed for obj in followed
                                            if not obj.latest_rate and not obj.has_in_recommend]
        followed_saw_title = [obj for obj in followed if obj.latest_rate]
    else:
        user_ratings_of_title = None
        current_rating = None
        is_favourite_for_user = None
        is_in_user_watchlist = None
        followed_can_take_recommendation = None
        followed_saw_title = None

    if request.method == 'POST':
        if not request.user.is_authenticated():
            messages.info(request, 'Only logged in users can add to watchlist or favourites')
            return redirect(title)

        watch, unwatch = request.POST.get('watch'), request.POST.get('unwatch')
        if watch or unwatch:
            obj_in_watchlist = Watchlist.objects.filter(user=request.user, title=title).first()
            alter_title_in_watchlist(request.user, title, obj_in_watchlist, watch, unwatch)

        fav, unfav = request.POST.get('fav'), request.POST.get('unfav')
        if fav or unfav:
            alter_title_in_favourites(request.user, title, fav, unfav)

        selected_users = request.POST.getlist('choose_followed_user')
        if selected_users:
            for choosen_user in selected_users:
                choosen_user = User.objects.get(username=choosen_user)
                if not Recommendation.objects.filter(user=choosen_user, title=title).exists()\
                        or not Rating.objects.filter(user=choosen_user, title=title).exists():
                    Recommendation.objects.create(user=choosen_user, sender=request.user, title=title)
                    messages.info(request, 'You recommended <a href="{}">{}</a> to <a href="{}">{}</a>'.format(
                        title.get_absolute_url(), title.name,
                        request.user.userprofile.get_absolute_url(), request.user.username
                    ), extra_tags='safe')

        new_rating = request.POST.get('rating')
        if new_rating:
            if current_rating and not request.POST.get('insert_as_new'):
                current_rating.rate = new_rating
                current_rating.save(update_fields=['rate'])
            elif current_rating and request.POST.get('insert_as_new'):
                ratings_from_today = Rating.objects.filter(user=request.user, title=title, rate_date=datetime.now())
                if ratings_from_today.exists():
                    # if you want to insert_as_new but it has been already rated today -> update only
                    ratings_from_today.update(rate=new_rating)
                else:
                    Rating.objects.create(user=request.user, title=title, rate=new_rating, rate_date=datetime.now())
            else:
                Rating.objects.create(user=request.user, title=title, rate=new_rating, rate_date=datetime.now())

        delete_rating = request.POST.get('delete_rating')
        if delete_rating:
            Rating.objects.filter(pk=request.POST.get('rating_pk'), user=request.user).delete()
        return redirect(title)

    avg_rate, rate_count = average_rating_of_title(title)
    context = {
        'entry': title,
        'user_ratings_of_title': user_ratings_of_title,
        'is_favourite_for_user': is_favourite_for_user,
        'is_in_user_watchlist': is_in_user_watchlist,
        'followed_can_take_recommendation': followed_can_take_recommendation,
        'followed_saw_title': followed_saw_title,
        'rate': {'avg': avg_rate, 'count': rate_count},
        'loop': (n for n in range(10, 0, -1)),
    }
    return render(request, 'title_details.html', context)


def title_edit(request, slug):
    title = get_object_or_404(Title, slug=slug)
    current_rating = Rating.objects.filter(user__username=request.user.username, title=title).first()
    if not request.user.is_authenticated() or not current_rating:
        messages.info(request, 'You can edit titles you have rated, you must be logged in')
        return redirect(title)
    form = EditRating(instance=current_rating)
    if request.method == 'POST':
        form = EditRating(request.POST)
        if form.is_valid():
            new_rate = form.cleaned_data.get('rate')
            new_date = form.cleaned_data.get('rate_date')
            message = ''
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
            return redirect(title)
    context = {
        'form': form,
        'entry': title,
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
        # todo order by average imdb/users ratings of their movies // popularity of their movies
    }
    return render(request, 'groupby_director.html', context)


def watchlist(request, username):
    user = get_object_or_404(User, username=username)
    user_watchlist = Watchlist.objects.filter(user=user)
    if request.method == 'POST':
        if not request.user == user:
            messages.info(request, 'You can change only your list')
            return redirect(user.userprofile.watchlist_url())
        if request.POST.get('watchlist_imdb_delete'):
            user_watchlist.filter(title__const=request.POST.get('const'), imdb=True, deleted=False).update(deleted=True)
        elif request.POST.get('watchlist_delete'):
            user_watchlist.filter(title__const=request.POST.get('const'), imdb=False).delete()
        elif request.POST.get('watchlist_imdb_readd'):
            user_watchlist.filter(title__const=request.POST.get('const'), imdb=True, deleted=True).update(deleted=False)
        return redirect(user.userprofile.watchlist_url())
    context = {
        'ratings': user_watchlist.filter(deleted=False),
        'title': 'See again',
        'archive': [e for e in user_watchlist if e.is_rated_with_later_date],
        'is_owner': request.user == user,
        'deleted': user_watchlist.filter(imdb=True, deleted=True),
    }
    return render(request, 'watchlist.html', context)


def favourite(request, username):
    user = get_object_or_404(User, username=username)
    user_favourites = Favourite.objects.filter(user=user)
    if request.method == 'POST':
        if not request.user == user:
            messages.info(request, 'You can change order only for your list')
            return redirect(user.userprofile.favourite_url())
        new_title_order = request.POST.get('item_order')
        if new_title_order:
            new_title_order = re.findall('tt\d{7}', new_title_order)
            for new_position, const in enumerate(new_title_order, 1):
                user_favourites.filter(title__const=const).update(order=new_position)
    context = {
        'ratings': user_favourites,
    }
    return render(request, 'favourite.html', context)


def add_title(request):
    return render(request, '')

