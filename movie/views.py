from django.shortcuts import render, get_object_or_404, redirect
from .models import Entry, Genre, Archive, Season, Episode, Type, Director
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models import Count
from django.core.urlresolvers import reverse
import datetime


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
                entries = entries.filter(
                    Q(name__icontains=query) | Q(year=query)
                ).distinct()
            else:
                entries = entries.filter(
                    Q(name__startswith=query) | Q(year=query)
                ).distinct()

        paginator = Paginator(entries, 50)
        page = request.GET.get('page')
        try:
            ratings = paginator.page(page)
        except PageNotAnInteger:
            ratings = paginator.page(1)
        except EmptyPage:
            ratings = paginator.page(paginator.num_pages)

        query_string = ''
        if query or selected_type:
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
        choosen_obj = get_object_or_404(Entry, const=request.POST.get('const'))
        if request.POST.get('watch'):
            choosen_obj.watch_again_date = datetime.datetime.now()
        elif request.POST.get('unwatch'):
            choosen_obj.watch_again_date = None
        choosen_obj.save()
        return redirect(reverse('explore'))


def book(request):
    return render(request, 'book.html')


def search(request):
    return render(request, 'search.html')


def about(request):
    return render(request, 'about.html', {'archive': Archive.objects.all()})


def entry_details(request, slug):
    requested_obj = get_object_or_404(Entry, slug=slug)

    if request.method == 'GET':
        context = {
            'entry': requested_obj,
            'archive': Archive.objects.filter(const=requested_obj.const).order_by('-rate_date'),
        }
        return render(request, 'entry_details.html', context)

    if request.method == 'POST':
        if request.POST.get('watch'):
            requested_obj.watch_again_date = datetime.datetime.now()
        elif request.POST.get('unwatch'):
            requested_obj.watch_again_date = None
        requested_obj.save()
        return redirect(reverse('entry_details', kwargs={'slug': slug}))


def entry_details_redirect(request, const):
    requested_obj = get_object_or_404(Entry, const=const)
    if requested_obj:
        return redirect(requested_obj)


def entry_groupby_year(request):
    from chart.charts import distribution_by_year
    context = {
        'year_count': Entry.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
        'chart': distribution_by_year()
    }
    return render(request, 'entry_groupby_year.html', context)


def entry_show_from_year(request, year):
    context = {
        'year': Entry.objects.filter(year=year).order_by('-rate', '-rate_imdb', '-votes'),
        'what_year': year,
    }
    return render(request, 'entry_show_from_year.html', context)


def entry_show_rated_in_month(request, year, month):
    import calendar
    context = {
        'year': Entry.objects.filter(rate_date__year=year, rate_date__month=month),
        'what_month_year': '{} {}'.format(calendar.month_name[int(month)], year),
    }
    return render(request, 'entry_show_rated_in_month.html', context)


def entry_groupby_genre(request):
    from chart.charts import chart_genres
    context = {
        'genre': Genre.objects.all().annotate(num=Count('entry')).order_by('-num'),
        'chart': chart_genres(),
    }
    return render(request, 'entry_groupby_genre.html', context)


def entry_show_from_genre(request, genre):
    context = {
        'titles_from_genre': Genre.objects.get(name=genre).entry_set.all(),
        'genre_name': genre,
    }
    return render(request, 'entry_show_from_genre.html', context)


def entry_show_from_rate(request, rate):
    context = {
        'entry': Entry.objects.filter(rate=rate).order_by('-rate_date'),
        'rate': rate,
    }
    return render(request, 'entry_show_from_rate.html', context)


def entry_groupby_director(request):
    context = {
        'director': Director.objects.filter(entry__type=Type.objects.get(name='movie')
                                            ).annotate(num=Count('entry')).order_by('-num')[:50],
    }
    return render(request, 'entry_groupby_director.html', context)


def entry_show_from_director(request, id):
    context = {
        'titles_from_director': Director.objects.get(id=id).entry_set.all().order_by('-rate_date'),
        'director_name': Director.objects.get(id=id).name,
    }
    return render(request, 'entry_show_from_director.html', context)


def watchlist(request):
    if request.method == 'GET':
        context = {
            # 'ratings': Entry.objects.filter(watch_again_date__isnull=True).order_by('-rate_date'),todo isnull problem
            'ratings': [e for e in Entry.objects.all() if e.watch_again_date],
            'history': Archive.objects.filter(watch_again_date__isnull=False)
        }
        return render(request, 'watchlist.html', context)

    if request.method == 'POST':
        choosen_obj = get_object_or_404(Entry, const=request.POST.get('const'))
        if request.POST.get('unwatch'):
            choosen_obj.watch_again_date = None
        choosen_obj.save()
        return redirect(reverse('watchlist'))

