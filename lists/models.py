from django.conf import settings
from django.db import models
from django.urls import reverse

from lists.mixins import LimitInstancesMixin


class Watchlist(LimitInstancesMixin, models.Model):
    create_date = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.ForeignKey('titles.Title', on_delete=models.CASCADE)
    imdb = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-create_date', )
        unique_together = ('user', 'title')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.title.year)

    def get_absolute_url(self):
        return reverse('watchlist', kwargs={'username': self.user.username})


class Favourite(LimitInstancesMixin, models.Model):
    create_date = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.ForeignKey('titles.Title', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order', '-create_date')
        unique_together = ('user', 'title')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.title.year)
