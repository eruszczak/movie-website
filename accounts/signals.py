import os
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_folder(sender, instance, **kwargs):
    """after registration create folder for user's files"""
    if kwargs['created']:
        directory = os.path.join(settings.MEDIA_ROOT, 'user_files', instance.username)
        if not os.path.exists(directory):
            os.makedirs(directory)
