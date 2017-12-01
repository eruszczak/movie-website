from datetime import datetime
from urllib.request import urlretrieve

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from os.path import join

from titles.constants import TITLE_CREW_JOB_CHOICES, TITLE_TYPE_CHOICES, SERIES
from titles.helpers import validate_rate
from shared.helpers import get_instance_file_path
from .managers import TitleQuerySet


class Keyword(models.Model):
    # name i think doesnt have to be unique in this case because the keywords are added by different people
    name = models.CharField(max_length=100, unique=True)
    # tmdb_id

    def __str__(self):
        return f'{self.name}'


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    # tmdb_id
    def __str__(self):
        return f'{self.name}'


class Person(models.Model):
    name = models.CharField(max_length=300)
    # tmdb_id

    def __str__(self):
        return f'{self.name}'


class CastTitle(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    title = models.ForeignKey('Title', on_delete=models.CASCADE)
    order = models.SmallIntegerField(default=0)
    character = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f'{self.person} in {self.title}'


class CastCrew(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    title = models.ForeignKey('Title', on_delete=models.CASCADE)
    job = models.IntegerField(choices=TITLE_CREW_JOB_CHOICES, blank=True, null=True)

    def __str__(self):
        return f'{self.person} in {self.title}'


class Title(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    source = JSONField(blank=True)

    # https://gist.github.com/cyface/3157428
    cast = models.ManyToManyField('Person', through='CastTitle', related_name='cast', blank=True)
    crew = models.ManyToManyField('Person', through='CastCrew', related_name='crew', blank=True)
    keywords = models.ManyToManyField('Keyword', blank=True)
    similar = models.ManyToManyField('Title', blank=True)
    genres = models.ManyToManyField('Genre')

    type = models.IntegerField(choices=TITLE_TYPE_CHOICES, blank=True, null=True)
    tmdb_id = models.CharField(unique=True, max_length=10)
    imdb_id = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350)
    overview = models.TextField(blank=True)
    release_date = models.DateField(blank=True, null=True)  # 1998-10-02
    runtime = models.IntegerField(blank=True, null=True)

    poster_path = models.CharField(max_length=300)
    poster_backdrop_title = models.ImageField(upload_to=get_instance_file_path, blank=True, null=True)
    poster_backdrop_user = models.ImageField(upload_to=get_instance_file_path, blank=True, null=True)
    poster_small = models.ImageField(upload_to=get_instance_file_path, blank=True, null=True)
    poster_card = models.ImageField(upload_to=get_instance_file_path, blank=True, null=True)

    # rate_imdb = models.FloatField(blank=True, null=True)
    # votes = models.IntegerField(blank=True, null=True)
    # plot = models.TextField(blank=True, null=True)
    # videos
    # images
    # tagline, overview?
    # todo: recommendations?
    # belongs_to_collection

    objects = TitleQuerySet.as_manager()

    class Meta:
        ordering = ()
        # ordering = ('-inserted_date', )

    def __str__(self):
        return f'{self.name} ({self.year})'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('title-detail', args=[self.imdb_id, self.slug])

    def get_folder_path(self, absolute=False):
        relative_title_folder_path = join('titles', self.imdb_id)
        if absolute:
            return join(settings.MEDIA_ROOT, relative_title_folder_path)
        return relative_title_folder_path

    def save_poster(self, file_name, url, poster_type):
        """download and save image to a one of poster_ fields"""
        poster_field = getattr(self, f'poster_{poster_type}')
        try:
            image = urlretrieve(url)[0]
        except (PermissionError, TypeError, ValueError) as e:
            print(e)
        else:
            poster_field.save(file_name, File(open(image, 'rb')))

    @property
    def imdb_url(self):
        return f'http://www.imdb.com/title/{self.imdb_id}/'

    @property
    def year(self):
        return self.release_date.year

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
        if not validate_rate(self.rate):
            raise ValidationError('Rating must be integer value between 1-10')

        if self.rate_date > datetime.today().date():
            raise ValidationError('Date cannot be in the future')

        if Rating.objects.filter(user=self.user, title=self.title, rate_date=self.rate_date).exists():
            raise ValidationError('Rating from this day already exists')

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
    title = models.ForeignKey('Title', on_delete=models.CASCADE, limit_choices_to={'type': SERIES})
    release_date = models.DateField(blank=True, null=True)  # 1998-10-02
    number = models.SmallIntegerField(default=1)
    episodes = models.SmallIntegerField(blank=True, null=True)
