from django.shortcuts import render, get_object_or_404
from django.db import connections

from .models import Entry, Genre


def index(request):
    context = {
        'last_rating': Entry.objects.all()[:100],
    }
    return render(request, 'movie/entry.html', context)

def about(request):
    return render(request, 'movie/about.html')


def entry_details(request, const):
    context = {
        'entry': get_object_or_404(Entry, const=const),
        # 'genres': get_object_or_404(Genre, const=const),
    }

    return render(request, 'movie/entry_details.html', context)

def entry_groupby_year(request):
    year_counter = []
    for y in Entry.objects.order_by('-year').values('year').distinct():
        year_counter.append((y['year'], Entry.objects.filter(year=y['year']).count()))
    context = {
        'year_counter': year_counter,
    }
    return render(request, 'movie/entry_groupby_year.html', context)

def entry_show_from_year(request, year):
    context = {
        'year': Entry.objects.order_by().filter(year=year)
    }
    return render(request, 'movie/entry_show_from_year.html', context)

def entry_groupby_genre(request):
    context = {
        'genre': Genre.objects.all()
    }
    return render(request, 'movie/entry_groupby_genre.html', context)

def entry_show_from_genre(request, genre):
    context = {
        'genre': Genre.objects.get(name=genre).entry_set.all()
    }
    return render(request, 'movie/entry_show_from_genre.html', context)