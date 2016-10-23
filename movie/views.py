from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q, Count, F
from django.contrib import messages
from .models import *
from .forms import EditRating
from utils.utils import paginate
import datetime
import calendar
import re
from django.views.generic import View


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
    # if request.method == 'POST':
    #     if not request.user.is_superuser:
    #         messages.info(request, 'Only admin can do this', extra_tags='alert-info')
    #         return redirect(reverse('explore'))
    #
    #     choosen_obj = get_object_or_404(Title, const=request.POST.get('const'))
    #     if 'watch' in request.POST.keys():
    #         choosen_obj.watch_again_date = datetime.datetime.now()
    #     elif 'unwatch' in request.POST.keys():
    #         choosen_obj.watch_again_date = None
    #     choosen_obj.save(update_fields=['watch_again_date'])
    #     return redirect(request.META.get('HTTP_REFERER'))
    entries = Rating.objects.filter(user=request.user)
    query = request.GET.get('q')
    selected_type = request.GET.get('select_type')
    if selected_type in 'movie series'.split():
        # entries = entries.filter(Q(type_id=Type.objects.get(name=selected_type).id))
        entries = entries.filter(Q(title__type__name=selected_type))
    if query:
        if len(query) > 2:
            entries = entries.filter(Q(title__name__icontains=query) | Q(title__year=query)).distinct()
        else:
            entries = entries.filter(Q(title__name__startswith=query) | Q(title__year=query)).distinct()

    page = request.GET.get('page')
    ratings = paginate(entries, page)

    query_string = ''
    if query and selected_type:
        select_type = '?select_type={}'.format(selected_type)
        q = '&q={}'.format(query)
        query_string = select_type + q + '&page='

    context = {
        'ratings': ratings,
        'query': query,
        'selected_type': selected_type,
        'query_string': query_string,
    }
    return render(request, 'entry.html', context)
#
#
# def book(request):
#     return render(request, 'book.html')
#
#
# def search(request):
#     return render(request, 'search.html')
#
#
# def about(request):
#     return render(request, 'about.html')
#
#
def entry_details(request, slug):
    requested_obj = get_object_or_404(Title, slug=slug)
#         if not request.user.is_superuser:
#             messages.info(request, 'Only admin can edit', extra_tags='alert-info')
#             return redirect(requested_obj)
        # every user can edit if have this rated but anons
    if request.method == 'POST':
        watch, unwatch = request.POST.get('watch'), request.POST.get('unwatch')
        fav_add, fav_remove = request.POST.get('fav_add'), request.POST.get('fav_remove')
        if watch or unwatch:
            if watch:
                Watchlist.objects.create(user=request.user, title=requested_obj)
            elif unwatch:
                to_delete = Watchlist.objects.get(user=request.user, title=requested_obj)
                if to_delete.imdb:
                    to_delete.deleted = True
                    to_delete.save()
                else:
                    to_delete.delete()
                # if not from imdb -> ok, delete.
        elif fav_add or fav_remove:
            if fav_add:
                Favourite.objects.create(user=request.user, title=requested_obj, order=Favourite.objects.all().count() + 1)
            elif fav_remove:
                to_delete = Favourite.objects.get(user=request.user, title=requested_obj)
                Favourite.objects.filter(order__gt=to_delete.order).update(order=F('order') - 1)
                to_delete.delete()
        return redirect(reverse('entry_details', kwargs={'slug': slug}))

    # user_current_rating = Rating.objects.filter(user=request.user).filter(title=requested_obj).first()
    user_current_rating = requested_obj.rating_set.filter(user=request.user).first()
    context = {
        'entry': requested_obj,
        'archive': Rating.objects.filter(user=request.user).filter(title=requested_obj),
        'favourite': Favourite.objects.filter(user=request.user).filter(title=requested_obj).first(),
        'watchlist': Watchlist.objects.filter(user=request.user).filter(title=requested_obj).first(),
        'link_month': reverse('entry_show_rated_in_month', kwargs={
            'year': user_current_rating.rate_date.year, 'month': user_current_rating.rate_date.month})
    }
    return render(request, 'entry_details.html', context)


def entry_edit(request, slug):
    requested_obj = get_object_or_404(Title, slug=slug)
    # if not request.user.is_superuser:
    #     messages.info(request, 'Only admin can edit', extra_tags='alert-info')
    #     return redirect(requested_obj)

    form = EditRating(instance=Rating.objects.filter(user=request.user, title=requested_obj).first())   # todo
    if request.method == 'POST':
        last_rating = Rating.objects.filter(user=request.user, title=requested_obj).first()
        form = EditRating(request.POST)
        if form.is_valid():
            new_rate = form.cleaned_data.get('rate')
            new_date = form.cleaned_data.get('rate_date')
            message = ''
            if last_rating.rate != int(new_rate):
                message += 'rating: {} changed for {}'.format(last_rating.rate, new_rate)
                last_rating.rate = new_rate
            if last_rating.rate_date != new_date:
                message += ', ' if message else ''
                message += 'date: {} changed for {}'.format(last_rating.rate_date, new_date)
                last_rating.rate_date = new_date
            if message:
                messages.success(request, message, extra_tags='alert-success')
                last_rating.save(update_fields=['rate', 'rate_date'])
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
    print(request.user, username)
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