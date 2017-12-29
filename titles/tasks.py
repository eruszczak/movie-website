from celery import shared_task


@shared_task
def task_run_daily_tmdb_tasks():
    from titles.tmdb_api import TmdbTaskRunner
    TmdbTaskRunner().run()


@shared_task
def task_get_details(title_pk):  # cannot pass a model instance: `Object of type 'Title' is not JSON serializable`
    from titles.tmdb_api import TitleDetailsGetter
    from titles.models import Title
    title = Title.objects.get(pk=title_pk)
    TitleDetailsGetter(title).run()


@shared_task
def task_update_title(title_pk):
    from titles.models import Title
    title = Title.objects.get(pk=title_pk)
    tmdb_instance = title.get_tmdb_instance()
    tmdb_instance(title=title).update()
