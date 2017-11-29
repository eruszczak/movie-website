from django.contrib.postgres.fields import JSONField
from django.db import models
from django.conf import settings

from .managers import TitleQuerySet


# todo: related names


class Keyword(models.Model):
    # name i think doesnt have to be unique in this case because the keywords are added by different people
    name = models.CharField(max_length=100, unique=True)
    # tmdb_id


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # tmdb_id

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=300)
    # tmdb_id


class CastTitle(models.Model):
    person = models.ForeignKey('Person')
    title = models.ForeignKey('Title')
    # cast id
    # order
    # character


class CastCrew(models.Model):
    # job
    # credit id
    pass


class Title(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    source = JSONField(blank=True)

    # videos
    # images
    # todo: recommendations?

    cast = models.ManyToManyField('Person', through='CastTitle', blank=True)
    crew = models.ManyToManyField('Person', through='CastCrew', blank=True)
    keyword = models.ManyToManyField('Keyword', blank=True)
    similar = models.ManyToManyField('Title', blank=True)  # todo need to set related name i guess because relation to self
    # director = models.ManyToManyField(Director)
    genres = models.ManyToManyField('Genre')
    # type = models.ForeignKey(Type, blank=True, null=True, on_delete=models.CASCADE)

    tmdb_id = models.CharField(unique=True, max_length=10)
    imdb_id = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350)
    overview = models.TextField(blank=True)
    release_date = models.DateField(blank=True, null=True)  # 1998-10-02
    runtime = models.IntegerField(blank=True, null=True)

    # img = models.ImageField(upload_to='poster', null=True, blank=True)
    # img_thumbnail = models.ImageField(null=True, blank=True)
    poster_path = models.CharField(max_length=300)
    # belongs_to_collection
    # tagline
    # video

    # no imdb average and count?


    objects = TitleQuerySet.as_manager()

    class Meta:
        ordering = ()
        # ordering = ('-inserted_date', )

    def __str__(self):
        return '{} {}'.format(self.name, self.year)

    @property
    def get_imdb_url(self):
        return ''


