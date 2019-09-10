from django.core.management.base import BaseCommand

from titles.tasks import task_run_daily_tmdb_tasks


class Command(BaseCommand):

    def handle(self, *args, **options):
        task_run_daily_tmdb_tasks.delay()


