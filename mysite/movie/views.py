from django.shortcuts import render, get_object_or_404
from django.db import connections

from .models import Entry
# def my_custom_sql():
#     last_ratings = "SELECT name, my_rate, imdb_rate, votes FROM Movie ORDER BY created DESC LIMIT 10"
#     cursor = connections['ratings'].cursor()    # may cause an error
#     cursor.execute(last_ratings)
#     return cursor
    # with connections['ratings'].cursor() as cursor:
    # cursor.execute('select name, my_rate, imdb_rate, votes from movie where type_id=8')
    # row = cursor.fetchall()
    # return row


def index(request):
    context = {
        'last_rating': Entry.objects.all(),
    }
    return render(request, 'movie/entry.html', context)

def about(request):
    return render(request, 'movie/about.html')


def entry_details(request, const):
    context = {
        'entry': get_object_or_404(Entry, const=const),
    }
    return render(request, 'movie/entry_details.html', context)

def entry_groupby_year(request):
    context = {
        'years': Entry.objects.order_by('-year').values('year').distinct(),
    }
    return render(request, 'movie/entry_groupby_year.html', context)

def entry_show_from_year(request, year):
    context = {
        'year': Entry.objects.order_by().filter(year=year)
    }
    return render(request, 'movie/entry_from_year.html', context)