def tmdb_image(func):
    poster_base = 'http://image.tmdb.org/t/p'

    def func_wrapper(self):
        return f'{poster_base}/{func(self)}/{self.image_path}'
    return func_wrapper
