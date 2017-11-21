from django.conf import settings
from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils import timezone

from titles.models import Title, Rating


class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    added_date = models.DateTimeField(default=timezone.now)
    imdb = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-added_date', )
        unique_together = ('user', 'title')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.title.year)

    def save(self, *args, **kwargs):
        if not self.id and self.imdb:
            # if there's later rating then it's not "active" anymore and should be deleted
            rated_later = Rating.objects.filter(user=self.user, title=self.title, rate_date__gte=self.added_date.date())
            if rated_later.exists():
                self.deleted = True
        super(Watchlist, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('watchlist', kwargs={'username': self.user.username})

    # todo
    @property
    def rated_after_days_diff(self):
        rating = Rating.objects.filter(user=self.user).filter(title=self.title, rate_date__gt=self.added_date).last()
        if rating:
            return {
                'rate': rating.rate,
                'days_diff': (rating.rate_date - self.added_date.date()).days
            }
        return None


class Favourite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    added_date = models.DateTimeField(default=timezone.now)
    order = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ('order', )
        unique_together = ('user', 'title')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.title.year)

    def get_absolute_url(self):
        return reverse('favourite', kwargs={'username': self.user.username})