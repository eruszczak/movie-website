from django.conf import settings
from os.path import join


class FolderPathMixin:
    MODEL_FOLDER_NAME = None
    INSTANCE_FOLDER_NAME = 'pk'

    def get_folder_path(self, absolute=False):
        """returns path of folder for model instance's files"""
        relative_model_folder_path = join(self.MODEL_FOLDER_NAME, getattr(self, self.INSTANCE_FOLDER_NAME))
        if absolute:
            return join(settings.MEDIA_ROOT, relative_model_folder_path)
        return relative_model_folder_path
