from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Subquery, IntegerField


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


class SubqueryCount(Subquery):
    """https://stackoverflow.com/a/47371514"""
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = IntegerField()


def fill_dictwriter_with_rating_qs(writer, ratings):
    for r in ratings:
        writer.writerow({
            'imdb_id': r.title.imdb_id,
            'rate_date': r.rate_date,
            'rate': r.rate
        })
