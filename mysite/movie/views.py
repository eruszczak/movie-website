from django.shortcuts import render
from django.db import connections

def my_custom_sql():
    cursor = connections['ratings'].cursor()
    cursor.execute('select name, my_rate, imdb_rate, votes from movie where type_id=8')
    return cursor
    # row = cursor.fetchall()
    # return row

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def index(requests):
    return render(requests, 'movie/movie.html', {'lists': my_custom_sql()})
    # return render(requests, 'movie/movie.html', {'list_dicts': dictfetchall(my_custom_sql())})