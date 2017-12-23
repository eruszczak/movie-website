from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Subquery, IntegerField


def tmdb_image(func):
    """
    Decorator around property. Usage:
    @property
    @tmdb_image
    def poster_backdrop_user(self):
        return IMAGE_SIZES['backdrop_user']
    Property will only return what kind of image it is. This decorator will return full TMDB hotlink.
    For development it returns static image.
    """

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
    """
    Decorator for APIView's post handler.
    class AddRatingAPIView(IsAuthenticatedMixin, GetTitleMixin, APIView):
        @instance_required
        def post(self, request, *args, **kwargs):
    APIView inherits GetTitleMixin so it will set self.title or return that `Ttle does not exist`
    """

    def func_wrapper(self, request, *args, **kwargs):
        message = self.set_instance(**kwargs)
        if message:
            return message

        return func(self, request, *args, **kwargs)

    return func_wrapper


class SubqueryCount(Subquery):
    """https://stackoverflow.com/a/47371514"""
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = IntegerField()
