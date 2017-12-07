from celery import shared_task

from tmdb.api import PopularMovies


@shared_task
def get_todays_popular_movies():
    PopularMovies().get()
