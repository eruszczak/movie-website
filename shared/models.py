from django.conf import settings
from os.path import join

from shared.helpers import create_folder_if_not_exists


class FolderPathMixin:
    """Mixin that provides methods of paths to model instance's folders"""
    MODEL_FOLDER_NAME = None
    ATTRIBUTE_FOR_FOLDER_NAME = 'pk'

    def get_folder_path(self, absolute=False, create=False):
        """If mixed with Account model, it will return eg.: /accounts/1/"""
        relative_path = join(self.MODEL_FOLDER_NAME, str(getattr(self, self.ATTRIBUTE_FOR_FOLDER_NAME)))
        absolute_path = join(settings.MEDIA_ROOT, relative_path)
        if create:
            create_folder_if_not_exists(absolute_path)

        if absolute:
            return absolute_path
        return relative_path

    def get_temp_folder_path(self, absolute=False, create=False):
        """If mixed with Account model, it will return eg.: /accounts/1/tmp"""
        instance_folder_root = self.get_folder_path()
        relative_path = join(instance_folder_root, 'tmp')
        absolute_path = join(settings.MEDIA_ROOT, relative_path)
        if create:
            # if instance_folder_root doesn't exist yet, it will be created too
            create_folder_if_not_exists(absolute_path)

        if absolute:
            return absolute_path
        return relative_path
