from django.shortcuts import render, get_object_or_404
from django.db import connections

from .models import Entry, Genre, Archive

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    entries = Entry.objects.all().order_by('-rate_date')
    paginator = Paginator(entries, 75)
    page = request.GET.get('page')
    try:
        ratings = paginator.page(page)
    except PageNotAnInteger:
        ratings = paginator.page(1)
    except EmptyPage:
        ratings = paginator.page(paginator.num_pages)
    context = {
        'ratings': ratings,
        'archive': Archive.objects.all(),
    }
    return render(request, 'movie/entry.html', context)


def about(request):
    return render(request, 'movie/about.html', {'archive': Archive.objects.all()})


def entry_details(request, const):
    context = {
        'entry': get_object_or_404(Entry, const=const),
        'archive': Archive.objects.filter(const=const),
    }

    return render(request, 'movie/entry_details.html', context)


def entry_groupby_year(request):
    year_counter = []
    for y in Entry.objects.order_by('-year').values('year').distinct():
        year_counter.append((y['year'], Entry.objects.filter(year=y['year']).count()))
    context = {
        'year_counter': year_counter,
        'counter': len(year_counter),
        'max': max(year_counter, key=lambda x: x[0])[0],
        'min': min(year_counter, key=lambda x: x[0])[0],
    }
    context['diff'] = int(context['max']) - int(context['min'])
    return render(request, 'movie/entry_groupby_year.html', context)


def entry_show_from_year(request, year):
    context = {
        'year': Entry.objects.order_by().filter(year=year),
        'counter': Entry.objects.order_by().filter(year=year).count(),
        'what_year': year,
    }
    return render(request, 'movie/entry_show_from_year.html', context)


def entry_groupby_genre(request):
    context = {
        'genre': Genre.objects.all(),
        'counter': Genre.objects.all().count()
    }
    return render(request, 'movie/entry_groupby_genre.html', context)


def entry_show_from_genre(request, genre):
    context = {
        'genre': Genre.objects.get(name=genre).entry_set.all(),
        'counter': Genre.objects.get(name=genre).entry_set.all().count(),
        'genre_name': genre,
    }
    return render(request, 'movie/entry_show_from_genre.html', context)
