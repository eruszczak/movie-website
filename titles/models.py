from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from common.sql_queries import avg_of_title_current_ratings
from titles.helpers import validate_rate
from .managers import TitleQuerySet


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('title-list') + '?g={}'.format(self.name)

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def get_absolute_url(self):
        return reverse('title-list') + '?d={}'.format(self.id)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def get_absolute_url(self):
        return reverse('title-list') + '?a={}'.format(self.id)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('title-list') + '?t={}'.format(self.name)

    def __str__(self):
        return self.name


class Title(models.Model):
    actor = models.ManyToManyField(Actor)
    genre = models.ManyToManyField(Genre)
    director = models.ManyToManyField(Director)
    type = models.ForeignKey(Type, blank=True, null=True, on_delete=models.CASCADE)

    const = models.CharField(unique=True, max_length=9)
    name = models.TextField(blank=True, null=True)

    rate_imdb = models.FloatField(blank=True, null=True)
    runtime = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    votes = models.IntegerField(blank=True, null=True)

    url_poster = models.URLField(blank=True, null=True, max_length=200)
    url_imdb = models.URLField(blank=True, null=True, max_length=200)
    url_tomato = models.URLField(blank=True, null=True, max_length=200)
    tomato_meter = models.IntegerField(blank=True, null=True)
    tomato_rating = models.FloatField(blank=True, null=True)
    tomato_reviews = models.IntegerField(blank=True, null=True)
    tomato_fresh = models.IntegerField(blank=True, null=True)
    tomato_rotten = models.IntegerField(blank=True, null=True)
    tomato_user_meter = models.IntegerField(blank=True, null=True)
    tomato_user_rating = models.FloatField(blank=True, null=True)
    tomato_user_reviews = models.IntegerField(blank=True, null=True)
    tomatoConsensus = models.TextField(blank=True, null=True)

    inserted_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    plot = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=300)
    img = models.ImageField(upload_to='poster', null=True, blank=True)
    img_thumbnail = models.ImageField(null=True, blank=True)

    objects = TitleQuerySet.as_manager()

    class Meta:
        ordering = ()
        # ordering = ('-inserted_date', )

    def __str__(self):
        return '{} {}'.format(self.name, self.year)

    def get_absolute_url(self):
        return reverse('title-detail', kwargs={'const': self.const, 'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.url_imdb = 'http://www.imdb.com/title/{}/'.format(self.const)
        super(Title, self).save(*args, **kwargs)

    @property
    def rate(self):
        """
        gets average of all current ratings for this title. if user1 rated this 5 and later 10 and user2 rated this 10
        then {count: 2, avg: 10} would be returned
        :return: eg. {count: 20, avg: 7.0}
        """
        return avg_of_title_current_ratings(self.id)

    @property
    def can_be_updated(self):
        return (timezone.now() - self.last_updated).seconds > 60 * 10


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    rate = models.IntegerField()
    rate_date = models.DateField()
    inserted_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'title', 'rate_date')
        ordering = ('-rate_date', '-inserted_date')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.rate_date)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        if not validate_rate(self.rate):
            raise ValidationError('Rating must be integer value between 1-10')

        if self.rate_date > datetime.today().date():
            raise ValidationError('Date cannot be in the future')

        if Rating.objects.filter(user=self.user, title=self.title, rate_date=self.rate_date).exists():
            raise ValidationError('Rating from this day already exists')

    def save(self, *args, **kwargs):
        """
        before creating new Rating, check if this title is in user's watchlist, if it is - delete it
        """
        # in_watchlist = Watchlist.objects.filter(user=self.user, title=self.title,
        #                                         added_date__date__lte=self.rate_date, deleted=False).first()
        # if in_watchlist:
        #     toggle_title_in_watchlist(unwatch=True, instance=in_watchlist)

        super(Rating, self).save(*args, **kwargs)

    @property
    def is_current_rating(self):
        return self == Rating.objects.filter(user=self.user, title=self.title).first()
