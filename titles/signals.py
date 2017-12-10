from django.apps import apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from shutil import rmtree

from shared.helpers import create_instance_folder


Title = apps.get_model('titles', 'Title')
Person = apps.get_model('titles', 'Person')
# Rating = apps.get_model('titles', 'Rating')


@receiver(post_save, sender=Title)
def create_title_folder(sender, instance, **kwargs):
    if kwargs['created']:
        create_instance_folder(instance)


@receiver(post_save, sender=Person)
def create_person_folder(sender, instance, **kwargs):
    if kwargs['created']:
        create_instance_folder(instance)


# @receiver(post_save, sender=Title)
# def create_title_folder(sender, instance, **kwargs):
#     if kwargs['created']:
#         create_instance_folder(instance)


# @receiver(post_delete, sender=Title)
# def delete_title_folder(sender, instance, **kwargs):
#     pass
    # rmtree(instance.get_folder_path(absolute=True), ignore_errors=True)
