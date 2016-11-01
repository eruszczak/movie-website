import calendar
import re

from django.contrib import messages
from django.db.models import Count, F
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from common.utils import paginate
from .forms import EditRating
from .models import Genre, Director, Actor, Type, Title, Rating, Watchlist, Favourite
from users.models import UserFollow
from recommend.models import Recommendation
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from datetime import datetime
from .utils.functions import alter_title_in_watchlist, alter_title_in_favourites


def home(request):
    all_movies = Rating.objects.filter(title__type__name='movie').order_by('-rate_date')
    all_series = Rating.objects.filter(title__type__name='series').order_by('-rate_date')
    # titles_count = Title.objects.all().count()
    if request.user.is_authenticated():
        # rated_titles = Title.objects.filter(rating__user__username='test').order_by('-rating__rate_date')
        # rated titles
        # rated_titles = Title.objects.all().rating_set.all()
        # user_ratings = Rating.objects.filter(user=request.user).order_by('-rate_date')
        # all_movies = user_ratings.filter(title__type__name='movie')
        # all_series = user_ratings.filter(title__type__name='series')
        all_movies = all_movies.filter(user=request.user)
        all_series = all_series.filter(user=request.user)
    context = {
        'ratings': all_movies,
        'last_movie': all_movies.first().title if all_movies else None,
        'last_series': all_series.first().title if all_series else None,
        'last_good_movie': all_movies.filter(rate__gte=9).first().title if all_movies.filter(rate__gte=9) else None,
        'movie_count': all_movies.count(),  # todo
        'series_count': all_series.count(),
        # 'search_movies': reverse('explore') + '?t=movie',
        # 'search_series': reverse('explore') + '?t=series',
        # see_more leads to explore with filtered user's ratings
    }
    if request.user.is_authenticated():
        context['search_movies'] = reverse('explore') + '?u={}&t=movies'.format(request.user.username)
        context['search_series'] = reverse('explore') + '?u={}&t=series'.format(request.user.username)
    else:
        context['total_movies'] = reverse('explore') + '?t=movie'
        context['total_series'] = reverse('explore') + '?t=series'
    return render(request, 'home.html', context)


def explore(request):
    if request.method == 'POST':
        requested_obj = get_object_or_404(Title, const=request.POST.get('const'))
        if not request.user.is_authenticated():
            messages.info(request, 'Only logged in users can add to watchlist or favourites', extra_tags='alert-info')
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
        # 'SELECT 1' will fail if for a user there are few ratings of the same title (just like it did in watchlist)
        titles = Title.objects.extra(select={
            'seen_by_user': """SELECT 1 FROM movie_rating as rating
                WHERE rating.title_id = movie_title.id AND rating.user_id = %s""",
            'has_in_watchlist': """SELECT 1 FROM movie_watchlist as watchlist
                WHERE watchlist.title_id = movie_title.id AND watchlist.user_id = %s AND watchlist.deleted = false""",
            'has_in_favourites': """SELECT 1 FROM movie_favourite as favourite
                WHERE favourite.title_id = movie_title.id AND favourite.user_id = %s"""
        }, select_params=[request.user.id] * 3)
    else:
        titles = Title.objects.all()
    query_string = ''

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
    if user:
        query_string += '{}={}&'.format('u', user)
        if request.GET.get('exclude_his'):
            titles = titles.exclude(rating__user__username=user)
            query_string += 'exclude_his=on&'
        elif request.GET.get('exclude_mine'):
            titles = titles.filter(rating__user__username=user).exclude(rating__user=request.user)
            query_string += 'exclude_mine=on&'
        else:
            titles = titles.filter(rating__user__username=user)

    page = request.GET.get('page')
    ratings = paginate(titles, page)

    if query_string:
        query_string = '?' + query_string
        query_string += 'page='

    # ratings = ((Rating.objects.filter(user=user, title=x).first(), x) for x in ratings)   # todo
    context = {
        'ratings': ratings,
        'query': query,
        'selected_type': selected_type,
        'genres': Genre.objects.annotate(num=Count('title')).order_by('-num'),
        # 'users': User.objects.annotate(num=Count('title')).order_by('-num'),
        'list_of_users': User.objects.all() if not request.user.is_authenticated() else User.objects.exclude(username=request.user.username),
        'query_string': query_string,
    }
    return render(request, 'explore.html', context)

# todo
# dont show in query string selected type if 0. IGNORE IT COMPLETLY
# dont show &q= if not using it
# you can sort by many fields


def title_details(request, slug):
    title = get_object_or_404(Title, slug=slug)
    if request.user.is_authenticated():
        user_ratings_of_title = Rating.objects.filter(user=request.user, title=title)
        current_rating = user_ratings_of_title.first()
        is_favourite_for_user = Favourite.objects.filter(user=request.user, title=title).exists()
        is_in_user_watchlist = Watchlist.objects.filter(user=request.user, title=title, deleted=False).exists()
        followed = [obj.user_followed for obj in UserFollow.objects.filter(user_follower=request.user)
                    if not Recommendation.objects.filter(user=obj.user_followed, title=title).exists()
                    and not Rating.objects.filter(user=obj.user_followed, title=title).exists()]
    else:
        user_ratings_of_title = None
        current_rating = None
        is_favourite_for_user = None
        is_in_user_watchlist = None
        followed = None

    if request.method == 'POST':
        if not request.user.is_authenticated():
            messages.info(request, 'Only logged in users can add to watchlist or favourites', extra_tags='alert-info')
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

        new_rating = request.POST.get('value')
        # insert_as_new_rate instead of editing todo
        if new_rating:
            if current_rating:
                current_rating.rate = new_rating
                current_rating.rate_date = datetime.today()
                current_rating.save(update_fields=['rate', 'rate_date'])
            else:
                Rating.objects.create(user=request.user, title=title, rate=new_rating, rate_date=datetime.now())

        delete_rating = request.POST.get('delete_rating')
        if delete_rating:
            current_rating.delete()
        return redirect(reverse('entry_details', kwargs={'slug': slug}))

    context = {
        'entry': title,
        'user_ratings_of_title': user_ratings_of_title,
        'is_favourite_for_user': is_favourite_for_user,
        'is_in_user_watchlist': is_in_user_watchlist,
        'followed_who_can_take_recommendation': followed,
        'rated_by': Rating.objects.filter(title=title).count(),  # todo count distinct for user
        'average': '1',
        'loop': (n for n in range(10, 0, -1)),
    }
    if current_rating:
        year, month = current_rating.rate_date.year, current_rating.rate_date.month
        context['link_month'] = reverse('entry_show_rated_in_month', kwargs={'year': year, 'month': month})
    return render(request, 'title_details.html', context)


def title_edit(request, slug):
    requested_obj = get_object_or_404(Title, slug=slug)
    current_rating = Rating.objects.filter(user__username=request.user.username, title=requested_obj).first()
    if not request.user.is_authenticated() or not current_rating:
        messages.info(request, 'You can edit titles you have rated, you must be logged in', extra_tags='alert-info')
        return redirect(requested_obj)

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
                messages.success(request, message, extra_tags='alert-success')
                current_rating.save(update_fields=['rate', 'rate_date'])
            else:
                messages.info(request, 'nothing changed', extra_tags='alert-info')
            return redirect(requested_obj)
    context = {
        'form': form,
        'entry': requested_obj,
    }
    return render(request, 'title_edit.html', context)


def title_details_redirect(request, const): # todo, id for very short url
    requested_obj = get_object_or_404(Title, const=const)
    return redirect(requested_obj)


def groupby_year(request):
    context = {
        'year_count': Title.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
    }
    return render(request, 'groupby_year.html', context)


def groupby_genre(request):
    context = {
        'genre': Genre.objects.annotate(num=Count('title')).order_by('-num'),   # todo count
    }
    return render(request, 'groupby_genre.html', context)


def groupby_director(request):
    context = {
        # 'director': Director.objects.filter(title__rating__user=request.user, title__type__name='movie').annotate(num=Count('title')).order_by('-num')[:50],
        'director': Director.objects.filter(title__type__name='movie').annotate(num=Count('title')).order_by('-num')[:50],
    }
    return render(request, 'groupby_director.html', context)


def titles_rated_in_month(request, year, month):
    # entries = Rating.objects.filter(user=request.user, rate_date__year=year, rate_date__month=month)
    # check what other people rated in that month // maybe day
    entries = Rating.objects.filter(rate_date__year=year, rate_date__month=month)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': '{} {}'.format(calendar.month_name[int(month)], year),
    }
    return render(request, 'title_from.html', context)


def titles_from_rate(request, rate):
    # entries = Rating.objects.filter(user=request.user, rate=rate)
    entries = Rating.objects.filter(rate=rate)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': rate,
    }
    return render(request, 'title_from.html', context)


def watchlist(request, username):
    is_owner = username == request.user.username
    user_watchlist = Watchlist.objects.filter(user__username=username)
    if request.method == 'POST':
        if not is_owner:
            messages.info(request, 'Only owner can do this', extra_tags='alert-info')
            return redirect(reverse('watchlist', kwargs={'username': username}))
        if request.POST.get('watchlist_imdb_delete'):
            user_watchlist.filter(title__const=request.POST.get('const'), imdb=True, deleted=False).update(deleted=True)
        elif request.POST.get('watchlist_delete'):
            user_watchlist.filter(title__const=request.POST.get('const'), imdb=False).delete()
        elif request.POST.get('watchlist_imdb_readd'):
            user_watchlist.filter(title__const=request.POST.get('const'), imdb=True, deleted=True).update(deleted=False)
        return redirect(reverse('watchlist', kwargs={'username': username}))
    context = {
        'ratings': user_watchlist.filter(deleted=False),
        'title': 'See again',
        'archive': [e for e in user_watchlist if e.is_rated_with_later_date],
        'is_owner': is_owner,
        'deleted': user_watchlist.filter(imdb=True, deleted=True),
    }
    return render(request, 'watchlist.html', context)


def favourite(request, username):
    is_owner = username == request.user.username
    user_favourites = Favourite.objects.filter(user__username=username)
    if request.method == 'POST':
        if not is_owner:
            messages.info(request, 'Only owner can do this', extra_tags='alert-info')
            return redirect(reverse('favourite', kwargs={'username': username}))
        item_order = request.POST.get('item_order')
        if item_order:
            item_order = re.findall('tt\d{7}', item_order)
            for new_position, item in enumerate(item_order, 1):
                user_favourites.filter(title__const=item).update(order=new_position)
    context = {
        'ratings': user_favourites,
    }
    return render(request, 'favourite.html', context)


def add_title(request):
    return render(request, '')


def rated_by_user(request, username):
    return render(request, '')
