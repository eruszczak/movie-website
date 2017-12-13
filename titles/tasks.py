from celery import shared_task

from tmdb.api import PopularMoviesTmdbTask


@shared_task
def get_todays_popular_movies():
    PopularMoviesTmdbTask().get()
