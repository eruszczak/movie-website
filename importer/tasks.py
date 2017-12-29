from celery import shared_task
from django.contrib.auth import get_user_model


@shared_task
def task_import(user_pk, file_path):
    from importer.utils import import_ratings_from_csv
    UserModel = get_user_model()
    user = UserModel.objects.get(pk=user_pk)
    import_ratings_from_csv(user, file_path)


@shared_task
def task_export(user_pk):
    from importer.utils import export_ratings
    UserModel = get_user_model()
    user = UserModel.objects.get(pk=user_pk)
    export_ratings(user)
