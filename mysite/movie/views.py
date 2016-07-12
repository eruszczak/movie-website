from django.shortcuts import render
from django.db import connections

def my_custom_sql():
    last_ratings = "SELECT name, my_rate, imdb_rate, votes FROM Movie ORDER BY created DESC LIMIT 10"
    # cursor = connections['ratings'].cursor()    # may cause an error
    with connections['ratings'].cursor() as cursor:
        cursor.execute(last_ratings)
        return cursor
    # cursor.execute('select name, my_rate, imdb_rate, votes from movie where type_id=8')
    # row = cursor.fetchall()
    # return row

# def dictfetchall(cursor):
#     "Return all rows from a cursor as a dict"
#     columns = [col[0] for col in cursor.description]
#     return [
#         dict(zip(columns, row))
#         for row in cursor.fetchall()
#     ]

def index(request):
    return render(request, 'movie/movie.html', {'lists': my_custom_sql()})
    # return render(requests, 'movie/movie.html', {'list_dicts': dictfetchall(my_custom_sql())})