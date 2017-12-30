from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now

from .helpers import tmdb_image, static_poster
from titles.constants import TITLE_CREW_JOB_CHOICES, TITLE_TYPE_CHOICES, SERIES, MOVIE, IMAGE_SIZES
from .managers import TitleQuerySet, RatingQuerySet
from titles.tasks import task_update_title, task_get_details


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

    @property
    @static_poster
    def picture_placeholder(self):
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


class CurrentlyWatchingTV(models.Model):
    update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.ForeignKey('Title', on_delete=models.CASCADE, limit_choices_to={'type': SERIES})

    def __str__(self):
        return f'{self.user} watching {self.title}'


class Title(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    has_details = models.BooleanField(default=False)
    getting_details = models.BooleanField(default=False)

    genres = models.ManyToManyField('Genre')
    keywords = models.ManyToManyField('Keyword', blank=True)
    cast = models.ManyToManyField('Person', through='CastTitle', related_name='cast', blank=True)
    crew = models.ManyToManyField('Person', through='CrewTitle', related_name='crew', blank=True)
    similar = models.ManyToManyField('Title', blank=True, related_name='similars')
    recommendations = models.ManyToManyField('Title', blank=True, related_name='recommends')

    collection = models.ForeignKey('Collection', blank=True, null=True, related_name='titles', on_delete=models.SET_NULL)

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
        ordering = ('-release_date', '-update_date')

    def __str__(self):
        return f"{self.name} ({self.year or '?'})"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('title-detail', args=[self.imdb_id, self.slug])

    def update(self):
        """
        Updates title through a button on title_detail page. It updates basic info and also calls get_details.
        Every authenticated user can request a title update by clicking button on title_detail.
        """
        task_update_title.delay(self.pk)

    def get_details(self):
        """
        Title by default is added without details (similar, recommendations, collection).
        Details are fetched when title without details is visited (through detail-view)
        """
        print(f'call tmdb updater task for {self.imdb_id}')
        task_get_details.delay(self.pk)

    def before_get_details(self):
        self.getting_details = True
        self.save()

    def after_get_details(self):
        self.getting_details = False
        self.has_details = True
        self.save()

    def get_tmdb_instance(self):
        from titles.tmdb_api import get_tmdb_concrete_class
        return get_tmdb_concrete_class(self.type)

    def can_be_updated(self, user):
        return not now().date() == self.update_date.date() or user.is_superuser

    @property
    @tmdb_image
    def poster_backdrop_user(self):
        return IMAGE_SIZES['backdrop_user']

    @property
    @static_poster
    def poster_backdrop_user_placeholder(self):
        return IMAGE_SIZES['backdrop_user']

    @property
    @tmdb_image
    def poster_backdrop_title(self):
        return IMAGE_SIZES['backdrop_title']

    @property
    @static_poster
    def poster_backdrop_title_placeholder(self):
        return IMAGE_SIZES['backdrop_title']

    @property
    @tmdb_image
    def poster_small(self):
        return IMAGE_SIZES['small']

    @property
    @static_poster
    def poster_small_placeholder(self):
        return IMAGE_SIZES['small']

    @property
    @tmdb_image
    def poster_card(self):
        return IMAGE_SIZES['card']

    @property
    @static_poster
    def poster_card_placeholder(self):
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
    def should_get_details(self):
        return not self.has_details and not self.getting_details

    # @property
    # def can_be_updated(self):
    #     seconds_since_last_update = (timezone.now() - self.update_date).seconds
    #     return seconds_since_last_update > 60 * 10


class Rating(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.ForeignKey('Title', on_delete=models.CASCADE)
    rate = models.IntegerField()
    rate_date = models.DateField()

    objects = RatingQuerySet.as_manager()

    class Meta:
        ordering = ('-rate_date', '-create_date')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.rate_date)


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
