from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from shared.helpers import create_instance_folder


@receiver(post_save, sender=apps.get_model('titles', 'Title'))
def create_user_folder(sender, instance, **kwargs):
    """after registration create folder for user's files"""
    if kwargs['created']:
        create_instance_folder(instance)
