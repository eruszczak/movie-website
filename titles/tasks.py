from celery import shared_task

from tmdb.api import PopularMoviesTmdbTask, run_tmdb_tasks


@shared_task
def run_daily_tmdb_tasks():
    run_tmdb_tasks()
    # PopularMoviesTmdbTask().get()


@shared_task
def test():
    print('x')