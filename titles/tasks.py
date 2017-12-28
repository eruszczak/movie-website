from celery import shared_task

from titles.models import Title
from titles.tmdb_api import TmdbTaskRunner


@shared_task
def task_run_daily_tmdb_tasks():
    TmdbTaskRunner().run()


@shared_task
def task_get_details(title_pk):  # cannot pass a model instance: `Object of type 'Title' is not JSON serializable`
    Title.objects.get(pk=title_pk).get_details()
