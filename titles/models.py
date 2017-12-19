from datetime import datetime

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from .helpers import tmdb_image
from titles.constants import TITLE_CREW_JOB_CHOICES, TITLE_TYPE_CHOICES, SERIES, MOVIE, IMAGE_SIZES
from .managers import TitleQuerySet


class Keyword(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.name}'


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return f"{reverse('title-list')}?genre={self.pk}"


class Person(models.Model):
    name = models.CharField(max_length=300)
    image_path = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('person-detail', args=[self.pk, self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    @tmdb_image
    def picture(self):
        return IMAGE_SIZES['small_person']


class CastTitle(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    title = models.ForeignKey('Title', on_delete=models.CASCADE)
    order = models.SmallIntegerField(default=0)
    character = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f'{self.person} in {self.title}'

    class Meta:
        ordering = ('order',)


class CrewTitle(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    title = models.ForeignKey('Title', on_delete=models.CASCADE)
    job = models.IntegerField(choices=TITLE_CREW_JOB_CHOICES, blank=True, null=True)

    def __str__(self):
        return f'{self.person} in {self.title}'


class Collection(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.name} - {self.titles.count()}'


class Popular(models.Model):
    update_date = models.DateField(unique=True)
    movies = models.ManyToManyField('Title', blank=True, related_name='popular_movies')
    tv = models.ManyToManyField('Title', blank=True, related_name='popular_tv')
    persons = models.ManyToManyField('Person', blank=True, related_name='popular')
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ('-update_date',)

    def __str__(self):
        return f'Popular on {self.update_date}'


class NowPlaying(models.Model):
    update_date = models.DateField(unique=True)
    titles = models.ManyToManyField('Title', blank=True, related_name='nowplaying')
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ('-update_date',)

    def __str__(self):
        return f'Now playing on {self.update_date}'


class Upcoming(models.Model):
    update_date = models.DateField(unique=True)
    titles = models.ManyToManyField('Title', blank=True, related_name='upcoming')
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ('-update_date',)

    def __str__(self):
        return f'Upcoming on {self.update_date}'


class Title(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    source = JSONField(blank=True)
    updated = models.BooleanField(default=False)
    being_updated = models.BooleanField(default=False)

    genres = models.ManyToManyField('Genre')
    keywords = models.ManyToManyField('Keyword', blank=True)
    cast = models.ManyToManyField('Person', through='CastTitle', related_name='cast', blank=True)
    crew = models.ManyToManyField('Person', through='CrewTitle', related_name='crew', blank=True)
    similar = models.ManyToManyField('Title', blank=True, related_name='similars')
    recommendations = models.ManyToManyField('Title', blank=True, related_name='recommends')

    collection = models.ForeignKey('Collection', blank=True, null=True, related_name='titles', on_delete=models.CASCADE)

    type = models.IntegerField(choices=TITLE_TYPE_CHOICES, blank=True, null=True)
    tmdb_id = models.CharField(unique=True, max_length=10)
    imdb_id = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350)
    overview = models.TextField(blank=True)
    release_date = models.DateField(blank=True, null=True)  # 1998-10-02
    runtime = models.IntegerField(blank=True, null=True)

    image_path = models.CharField(max_length=300)

    objects = TitleQuerySet.as_manager()

    class Meta:
        ordering = ()

    def __str__(self):
        return f'{self.name} ({self.year})'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('title-detail', args=[self.imdb_id, self.slug])

    def call_update_task(self, force=False):
        """
        Calls celery task if title haven't been updated yet. Triggered after title was visited by someone.
        Can pass `force=True` so title will be updated even if it was updated before
        """
        from titles.tasks import task_update_title
        if (not self.updated and not self.being_updated) or force:
            print('call tmdb updater task for tmdb_id', self.tmdb_id)
            task_update_title.delay(self.pk)

    def update(self):
        from titles.tmdb_api import TitleUpdater
        TitleUpdater(self)

    def before_update(self):
        self.being_updated = True
        self.save()

    def after_update(self):
        self.being_updated = False
        self.updated = True
        self.save()

    @property
    @tmdb_image
    def poster_backdrop_user(self):
        return IMAGE_SIZES['backdrop_user']

    @property
    @tmdb_image
    def poster_backdrop_title(self):
        return IMAGE_SIZES['backdrop_title']

    @property
    @tmdb_image
    def poster_small(self):
        return IMAGE_SIZES['small']

    @property
    @tmdb_image
    def poster_card(self):
        return IMAGE_SIZES['card']

    @property
    def is_movie(self):
        return self.type == MOVIE

    @property
    def is_in_collection(self):
        return self.collection

    @property
    def imdb_url(self):
        return f'http://www.imdb.com/title/{self.imdb_id}/'

    @property
    def tmdb_url(self):
        return f'http://www.themoviedb.org/movie/{self.tmdb_id}/'

    @property
    def year(self):
        try:
            return self.release_date.year
        except AttributeError:
            return ''

    @property
    def average_rate(self):
        return 0.0
        # """
        # gets average of all current ratings for this title. if user1 rated this 5 and later 10 and user2 rated this 10
        # then {count: 2, avg: 10} would be returned
        # :return: eg. {count: 20, avg: 7.0}
        # """
        # return avg_of_title_current_ratings(self.id)

    @property
    def can_be_updated(self):
        seconds_since_last_update = (timezone.now() - self.update_date).seconds
        return seconds_since_last_update > 60 * 10


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
        if not self.validate_rate():
            raise ValidationError('Rating must be integer value between 1-10')

        if self.rate_date > datetime.today().date():
            raise ValidationError('Date cannot be in the future')

        if Rating.objects.filter(user=self.user, title=self.title, rate_date=self.rate_date).exists():
            raise ValidationError('Rating from this day already exists')

    def validate_rate(self):
        """rating must be integer 1-10"""
        try:
            rate = int(self.rate)
        except (ValueError, TypeError):
            return False
        return 0 < rate < 11

    # def save(self, *args, **kwargs):
    #     """
    #     before creating new Rating, check if this title is in user's watchlist, if it is - delete it
    #     """
    #     # in_watchlist = Watchlist.objects.filter(user=self.user, title=self.title,
    #     #                                         added_date__date__lte=self.rate_date, deleted=False).first()
    #     # if in_watchlist:
    #     #     toggle_title_in_watchlist(unwatch=True, instance=in_watchlist)
    #
    #     super(Rating, self).save(*args, **kwargs)

    # @property
    # def is_current_rating(self):
    #     return self == Rating.objects.filter(user=self.user, title=self.title).first()


class Season(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        limit_choices_to={'type': SERIES},
        related_name='seasons'
    )
    release_date = models.DateField(blank=True, null=True)  # 1998-10-02
    number = models.SmallIntegerField(default=1)
    episodes = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        ordering = ('-number',)
