from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from shared.helpers import create_instance_folder


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_folder(sender, instance, **kwargs):
    """after registration create folder for user's files"""
    if kwargs['created']:
        create_instance_folder(instance)


# @receiver(post_save, sender=User)
# def clean_user_files(sender, instance, **kwargs):
#     """when user uploads new avatar or csv, delete previous files because they won't be used anymore"""
#     picture_changed = instance.picture != instance.__original_picture
#     csv_changed = instance.csv_ratings != instance.__original_csv
#     if picture_changed:
#         instance.delete_previous_file('picture')
#     if csv_changed:
#         instance.delete_previous_file('csv')

# def delete_previous_file(self, what_to_delete):
#     """
#     if user in his settigns uploads new avatar/ratings.csv or replaces it, previous file is deleted
#     """
#     user_folder = os.path.join(MEDIA_ROOT, 'user_files', self.username)
#     for file in os.listdir(user_folder):
#         if self.get_extension_condition(file, what_to_delete):
#             path = os.path.join(user_folder, file)
#             os.remove(path)
