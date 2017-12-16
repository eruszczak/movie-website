from celery import shared_task

from titles.tmdb_api import TmdbTaskRunner


@shared_task
def run_daily_tmdb_tasks():
    TmdbTaskRunner().run()


@shared_task
def test():
    print('x')
