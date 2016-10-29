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


def home(request):
    # manager for getting user's ratings
    # show others ratings maybe
    all_movies = Rating.objects.filter(user=request.user, title__type__name='movie')
    all_series = Rating.objects.filter(user=request.user, title__type__name='series')
    random = Rating.objects.all().first()
    random_title = Title.objects.all().first()
    context = {
        'ratings': all_movies,
        'last_movie': all_movies[0].title if all_movies else random_title,
        'last_series': all_series[0].title if all_series else random_title,
        'last_good': all_movies.filter(rate__gte=5)[0].title if all_movies else random_title,
        'movie_count': all_movies.count(),
        'series_count': all_series.count(),
        # 'search_movies': reverse('explore') + '?select_type=movie&q=',
        # 'search_series': reverse('explore') + '?select_type=series&q=',
    }
    return render(request, 'home.html', context)


def explore(request):
    user = request.user if request.user.is_authenticated() else None

    if request.method == 'POST':
        # user_favourites = Favourite.objects.filter(user=request.user)
        requested_obj = get_object_or_404(Title, const=request.POST.get('const'))
        if not request.user.is_authenticated():
            messages.info(request, 'Only logged in users can add to watchlist or favourites', extra_tags='alert-info')
            return redirect(request.META.get('HTTP_REFERER'))

        watch, unwatch = request.POST.get('watch'), request.POST.get('unwatch')
        # fav_add, fav_remove = request.POST.get('fav_add'), request.POST.get('fav_remove')
        if watch:
            Watchlist.objects.create(user=request.user, title=requested_obj)
        elif unwatch:
            to_delete = Watchlist.objects.get(user=request.user, title=requested_obj)
            if to_delete.imdb:
                to_delete.deleted = True
                to_delete.save(update_fields=['deleted'])
            else:
                to_delete.delete()
        # if fav_add:
        #     Favourite.objects.create(user=request.user, title=requested_obj, order=user_favourites.count() + 1)
        # elif fav_remove:
        #     to_delete = user_favourites.filter(title=requested_obj).first()
        #     user_favourites.filter(order__gt=to_delete.order).update(order=F('order') - 1)
        #     to_delete.delete()
        return redirect(request.META.get('HTTP_REFERER'))

    entries = Rating.objects.all().order_by('title__inserted_date').distinct('title__inserted_date')
    # entries = Title.objects.all()
    # because i dont have a access to full ratings there
    # hmm can change order later
    # how to get for a title info about rating
    print(entries)
    query = request.GET.get('q')
    types = {'0': '', '1': 'movie', '2': 'series'}

    selected_type = request.GET.get('t', '0')
    if selected_type in ('1', '2'):
        entries = entries.filter(Q(type__name=types[selected_type]))
    if query:
        if len(query) > 2:
            entries = entries.filter(Q(name__icontains=query) | Q(year=query)).distinct()
        else:
            entries = entries.filter(Q(name__startswith=query) | Q(year=query)).distinct()
    page = request.GET.get('page')
    ratings = paginate(entries, page)

    # query_string = ''
    # if query and request.GET.get('select_type'):
    #     select_type = '?select_type={}'.format(selected_type)
    #     q = '&q={}'.format(query)
    #     query_string = select_type + q + '&page='

    # ratings = ((Rating.objects.filter(user=user, title=x).first(), x) for x in ratings)   # todo

    context = {
        'ratings': ratings,
        'query': query,
        'selected_type': types[selected_type]
        # 'query_string': query_string,
    }
    return render(request, 'entry.html', context)

# todo
# dont show in query string selected type if 0. IGNORE IT COMPLETLY
# dont show &q= if not using it
# show all titles
# you can sort by many fields
# can see which titles were rated / favourited / watchlisted



# def book(request):
#     return render(request, 'book.html')
# def search(request):
#     return render(request, 'search.html')
# def about(request):
#     return render(request, 'about.html')


def entry_details(request, slug):
    requested_obj = get_object_or_404(Title, slug=slug)
    user = request.user if request.user.is_authenticated() else None
    user_favourites = Favourite.objects.filter(user=user)
    user_watchlist = Watchlist.objects.filter(user=user)
    user_ratings_of_requested_obj = Rating.objects.filter(user=user, title=requested_obj)
    current_rating = user_ratings_of_requested_obj.first()
    if request.method == 'POST':
        if not request.user.is_authenticated():
            messages.info(request, 'Only logged in users can add to watchlist or favourites', extra_tags='alert-info')
            return redirect(requested_obj)

        watch, unwatch = request.POST.get('watch'), request.POST.get('unwatch')
        fav_add, fav_remove = request.POST.get('fav_add'), request.POST.get('fav_remove')
        if watch:
            Watchlist.objects.create(user=request.user, title=requested_obj)
        elif unwatch:
            to_delete = Watchlist.objects.get(user=request.user, title=requested_obj)
            if to_delete.imdb:
                to_delete.deleted = True
                to_delete.save(update_fields=['deleted'])
            else:
                to_delete.delete()
        elif fav_add:
            Favourite.objects.create(user=request.user, title=requested_obj, order=user_favourites.count() + 1)
        elif fav_remove:
            to_delete = user_favourites.filter(title=requested_obj).first()
            user_favourites.filter(order__gt=to_delete.order).update(order=F('order') - 1)
            to_delete.delete()

        selected_users = request.POST.getlist('choose_followed_user')
        if selected_users:
            for choosen_user in selected_users:
                choosen_user = User.objects.get(username=choosen_user)
                if not Recommendation.objects.filter(user=choosen_user, title=requested_obj).exists()\
                        or not Rating.objects.filter(user=choosen_user, title=requested_obj).exists():
                    Recommendation.objects.create(user=choosen_user, sender=user, title=requested_obj)

        new_rating = request.POST.get('value')
        if new_rating:
            if current_rating:
                current_rating.rate = new_rating
                current_rating.save(update_fields=['rate'])
            else:
                Rating.objects.create(user=user, title=requested_obj, rate=new_rating, rate_date=datetime.now())

        delete_rating = request.POST.get('delete_rating')
        if delete_rating:
            current_rating.delete()
        return redirect(reverse('entry_details', kwargs={'slug': slug}))

    # todo: below is a ugly way of doing things
    followed_by_user = UserFollow.objects.filter(user_follower=user).values_list('user_followed', flat=True)
    followed_who_saw_this_title = Rating.objects.filter(user__id__in=followed_by_user, title=requested_obj).values_list('user__id', flat=True)
    followed_who_have_it_in_recommended = Recommendation.objects.filter(user__id__in=followed_by_user, title=requested_obj).values_list('user_id', flat=True)
    context = {
        'entry': requested_obj,
        'archive': user_ratings_of_requested_obj,
        'favourite': user_favourites.filter(title=requested_obj).first(),
        'watchlist': user_watchlist.filter(title=requested_obj).first(),
        # 'follows': UserFollow.objects.filter(user_follower=user),
        'follows': UserFollow.objects.filter(user_follower=user).exclude(user_followed__id__in=followed_who_saw_this_title).exclude(user_followed__id__in=followed_who_have_it_in_recommended),
        'rated_by': Rating.objects.filter(title=requested_obj).count(),  # todo count distinct for user
        'average': '1',
        'loop': (n for n in range(10, 0, -1)),
    }
    if current_rating:
        year, month = current_rating.rate_date.year, current_rating.rate_date.month
        context['link_month'] = reverse('entry_show_rated_in_month', kwargs={'year': year, 'month': month})
    return render(request, 'entry_details.html', context)


def entry_edit(request, slug):
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
    return render(request, 'entry_edit.html', context)


def entry_details_redirect(request, const):
    requested_obj = get_object_or_404(Title, const=const)
    return redirect(requested_obj)


def entry_groupby_year(request):
    context = {
        'year_count': Title.objects.filter(rating__user=request.user).values('year').annotate(the_count=Count('year')).order_by('-year'),
    }
    return render(request, 'entry_groupby_year.html', context)


def entry_groupby_genre(request):
    context = {
        'genre': Genre.objects.filter(title__rating__user=request.user).annotate(num=Count('title')).order_by('-num'),  # todo, genre.set all?
    }
    return render(request, 'entry_groupby_genre.html', context)


def entry_groupby_director(request):
    context = {
        'director': Director.objects.filter(title__rating__user=request.user, title__type__name='movie'
                                            ).annotate(num=Count('title')).order_by('-num')[:50],
    }
    return render(request, 'entry_groupby_director.html', context)


def entry_show_from_year(request, year):
    # entries = Title.objects.filter(year=year).order_by('-rate', '-rate_imdb', '-votes')
    entries = Title.objects.filter(rating__user=request.user, year=year)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': year,
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_rated_in_month(request, year, month):
    entries = Rating.objects.filter(user=request.user, rate_date__year=year, rate_date__month=month)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': '{} {}'.format(calendar.month_name[int(month)], year),
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_from_genre(request, genre):
    # entries = Genre.objects.get(name=genre).title_set.filter(rating__user=request.user)
    entries = Rating.objects.filter(user=request.user, title__genre__name=genre)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': genre,
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_from_rate(request, rate):
    entries = Rating.objects.filter(user=request.user, rate=rate)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': rate,
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_from_director(request, pk):
    # entries = Director.objects.get(id=pk).title_set.filter(rating__user=request.user)
    entries = Rating.objects.filter(user=request.user, title__director__id=pk)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': Director.objects.get(id=pk).name,
    }
    return render(request, 'entry_show_from.html', context)


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
