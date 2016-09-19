from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.contrib import messages
from .models import Entry, Genre, Archive, Type, Director, Watchlist
from .forms import EditEntry
from utils.utils import paginate
import datetime
import calendar


def home(request):
    all_movies = Entry.objects.filter(type=Type.objects.get(name='movie').id)
    all_series = Entry.objects.filter(type=Type.objects.get(name='series').id)
    context = {
        'ratings': Entry.objects.all().order_by('-rate_date')[:10],
        'info': {
            'last_movie': all_movies.order_by('-rate_date')[0],
            'last_series': all_series.order_by('-rate_date')[0],
            'last_good': all_movies.filter(rate__gte=9).order_by('-rate_date')[0],
            'movie_count': all_movies.count(),
            'series_count': all_series.count(),
            'search_movies': reverse('explore') + '?select_type=movie&q=',
            'search_series': reverse('explore') + '?select_type=series&q=',
        }
    }
    return render(request, 'home.html', context)


def explore(request):
    if request.method == 'GET':
        entries = Entry.objects.all().order_by('-rate_date', '-inserted_date')
        query = request.GET.get('q')
        selected_type = request.GET.get('select_type')
        if selected_type in 'movie series'.split():
            entries = entries.filter(Q(type_id=Type.objects.get(name=selected_type).id))
        if query:
            if len(query) > 2:
                entries = entries.filter(Q(name__icontains=query) | Q(year=query)).distinct()
            else:
                entries = entries.filter(Q(name__startswith=query) | Q(year=query)).distinct()

        page = request.GET.get('page')
        ratings = paginate(entries, page)

        query_string = ''
        if query and selected_type:
            select_type = '?select_type={}'.format(selected_type)
            q = '&q={}'.format(query)
            query_string = select_type + q + '&page='

        context = {
            'ratings': ratings,
            'archive': Archive.objects.all(),
            'query': query,
            'selected_type': selected_type,
            'query_string': query_string,
        }
        return render(request, 'entry.html', context)

    if request.method == 'POST':
        if not request.user.is_superuser:
            messages.info(request, 'Only admin can do this', extra_tags='alert-info')
            return redirect(reverse('explore'))

        choosen_obj = get_object_or_404(Entry, const=request.POST.get('const'))
        if request.POST.get('watch'):
            choosen_obj.watch_again_date = datetime.datetime.now()
        elif request.POST.get('unwatch'):
            choosen_obj.watch_again_date = None
        choosen_obj.save()
        return redirect(request.META.get('HTTP_REFERER'))


def book(request):
    return render(request, 'book.html')


def search(request):
    return render(request, 'search.html')


def about(request):
    return render(request, 'about.html')


def entry_details(request, slug):
    requested_obj = get_object_or_404(Entry, slug=slug)
    if request.method == 'GET':
        context = {
            'entry': requested_obj,
            'archive': Archive.objects.filter(const=requested_obj.const).order_by('-rate_date'),
            'link_month': reverse('entry_show_rated_in_month',
                                  kwargs={'year': requested_obj.rate_date.year, 'month': requested_obj.rate_date.month})
        }
        return render(request, 'entry_details.html', context)

    if request.method == 'POST':
        if not request.user.is_superuser:
            messages.info(request, 'Only admin can edit', extra_tags='alert-info')
            return redirect(requested_obj)

        if request.POST.get('watch'):
            requested_obj.watch_again_date = datetime.datetime.now()
        elif request.POST.get('unwatch'):
            requested_obj.watch_again_date = None
        requested_obj.save()
        return redirect(reverse('entry_details', kwargs={'slug': slug}))


def entry_edit(request, slug):
    requested_obj = get_object_or_404(Entry, slug=slug)
    if not request.user.is_superuser:
        messages.info(request, 'Only admin can edit', extra_tags='alert-info')
        return redirect(requested_obj)

    form = EditEntry(instance=requested_obj)
    if request.method == 'POST':
        form = EditEntry(request.POST)
        if form.is_valid():
            new_rate = form.cleaned_data.get('rate')
            new_date = form.cleaned_data.get('rate_date')
            message = ''
            if requested_obj.rate != int(new_rate):
                message += 'rating: {} changed for {}'.format(requested_obj.rate, new_rate)
                requested_obj.rate = new_rate
            if requested_obj.rate_date != new_date:
                message += ', ' if message else ''
                message += 'date: {} changed for {}'.format(requested_obj.rate_date, new_date)
                requested_obj.rate_date = new_date
            if message:
                messages.success(request, message, extra_tags='alert-success')
            else:
                messages.info(request, 'nothing changed', extra_tags='alert-info')
            requested_obj.save(update_fields=['rate', 'rate_date'])
            return redirect(requested_obj)
    context = {
        'form': form,
        'entry': requested_obj,
    }
    return render(request, 'entry_edit.html', context)


def entry_details_redirect(request, const):
    requested_obj = get_object_or_404(Entry, const=const)
    return redirect(requested_obj)


def entry_groupby_year(request):
    context = {
        'year_count': Entry.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
    }
    return render(request, 'entry_groupby_year.html', context)


def entry_groupby_genre(request):
    context = {
        'genre': Genre.objects.all().annotate(num=Count('entry')).order_by('-num'),
    }
    return render(request, 'entry_groupby_genre.html', context)


def entry_groupby_director(request):
    context = {
        'director': Director.objects.filter(entry__type=Type.objects.get(name='movie')).annotate(num=Count('entry')).order_by('-num')[:50],
    }
    return render(request, 'entry_groupby_director.html', context)


def entry_show_from_year(request, year):
    entries = Entry.objects.filter(year=year).order_by('-rate', '-rate_imdb', '-votes')
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': year,
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_rated_in_month(request, year, month):
    entries = Entry.objects.filter(rate_date__year=year, rate_date__month=month)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': '{} {}'.format(calendar.month_name[int(month)], year),
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_from_genre(request, genre):
    entries = Genre.objects.get(name=genre).entry_set.all()
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': genre,
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_from_rate(request, rate):
    entries = Entry.objects.filter(rate=rate).order_by('-rate_date')
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': rate,
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_from_director(request, pk):
    entries = Director.objects.get(id=pk).entry_set.all().order_by('-rate_date')
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': Director.objects.get(id=pk).name,
    }
    return render(request, 'entry_show_from.html', context)


def watch_again(request):
    if request.method == 'GET':
        context = {
            # 'ratings': Entry.objects.filter(watch_again_date__isnull=True).order_by('-rate_date'),todo isnull problem
            'ratings': [e for e in Entry.objects.all() if e.watch_again_date],
            'history': Archive.objects.filter(watch_again_date__isnull=False),
            'title': 'See again'
        }
        return render(request, 'watch_again.html', context)

    if request.method == 'POST':
        if not request.user.is_superuser:
            messages.info(request, 'Only admin can do this', extra_tags='alert-info')
            return redirect(reverse('watchlist'))
        choosen_obj = get_object_or_404(Entry, const=request.POST.get('const'))
        if request.POST.get('unwatch'):
            choosen_obj.watch_again_date = None
        choosen_obj.save()
        return redirect(reverse('watchlist'))


def watchlist(request):
    context = {
        'watchlist': Watchlist.objects.filter().order_by('active', '-deleted_after_watched'),
        'title': 'IMDb Watchlist'
    }
    return render(request, 'watchlist.html', context)

