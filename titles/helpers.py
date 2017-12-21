from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static


def tmdb_image(func):

    def func_wrapper(self):
        if settings.DEBUG:
            if self.__class__.__name__ == 'Person':
                # for developing I want to display different w185 placeholder for Person
                return static('img/posters/w185_and_h278_bestv2_person.jpg')
            return static(f'img/posters/{func(self)}.jpg')

        if self.image_path:
            return f'http://image.tmdb.org/t/p/{func(self)}/{self.image_path}'

        # todo: raise Exception('Placeholder is needed')

    return func_wrapper


def instance_required(func):

    def func_wrapper(self, request, *args, **kwargs):
        message = self.set_instance(**kwargs)
        if message:
            return message

        return func(self, request, *args, **kwargs)

    return func_wrapper
