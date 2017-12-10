from django.contrib.staticfiles.templatetags.staticfiles import static


def tmdb_image(func):
    local = True

    def func_wrapper(self):
        if local:
            return static(f'img/posters/{func(self)}.jpg')
        if self.image_path:
            return f'http://image.tmdb.org/t/p/{func(self)}/{self.image_path}'

        # raise Exception('Placeholder is needed')

    return func_wrapper
