from django.apps import apps
from django.db.models import F
from django.db.models.signals import pre_delete
from django.dispatch import receiver

Favourite = apps.get_model('lists', 'Favourite')


@receiver(pre_delete, sender=Favourite)
def create_user_folder(sender, instance, **kwargs):
    """decrease order of all favourite titles that have order bigger than removed instance"""
    Favourite.objects.filter(user=instance.user, order__gt=instance.order).update(order=F('order') - 1)
