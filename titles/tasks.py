from celery import shared_task

from titles.models import Title
from titles.tmdb_api import TmdbTaskRunner


@shared_task
def task_run_daily_tmdb_tasks():
    TmdbTaskRunner().run()


@shared_task
def task_get_details(title_pk):  # cannot pass a model instance: `Object of type 'Title' is not JSON serializable`
    from titles.tmdb_api import TitleDetailsGetter
    title = Title.objects.get(pk=title_pk)
    TitleDetailsGetter(title)


@shared_task
def task_update_title(title_pk):
    title = Title.objects.get(pk=title_pk)
    tmdb_instance = title.get_tmdb_instance()
    tmdb_instance(title=title, update=True).get_or_create()
