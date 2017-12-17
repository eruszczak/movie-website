from celery import shared_task

from titles.models import Title
from titles.tmdb_api import TmdbTaskRunner


@shared_task
def task_run_daily_tmdb_tasks():
    TmdbTaskRunner().run()


@shared_task
def test():
    print('x')


@shared_task
def task_update_title(title_pk):  # cannot pass a model instance: `Object of type 'Title' is not JSON serializable`
    Title.objects.get(pk=title_pk).update()
