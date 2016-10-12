from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.db import models
from django.db.models import Q
import datetime
import sys
from django.contrib.auth.models import User

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('entry_show_from_genre', kwargs={'genre': self.name})

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    actor = models.ManyToManyField(Actor)
    genre = models.ManyToManyField(Genre)
    director = models.ManyToManyField(Director)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)

    const = models.CharField(unique=True, max_length=7)
    name = models.TextField()

    rate_imdb = models.FloatField(blank=True, null=True)
    runtime = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    votes = models.IntegerField(blank=True, null=True)

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
    slug = models.SlugField(unique=True, max_length=255)
    img = models.ImageField(upload_to='poster', null=True, blank=True)  # changed path, need a fix
    watch_again_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.name, self.year)

    def get_absolute_url(self):
        return reverse('entry_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify('{} {}'.format(self.name, self.year))
        if not self.url_imdb:
            self.url_imdb = 'http://www.imdb.com/title/{}/'.format(self.const)
        super(Title, self).save(*args, **kwargs)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    rate = models.IntegerField(blank=True, null=True)
    rate_date = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'title', 'rate', 'rate_date')



# class Season(models.Model):
#     entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
#     number = models.IntegerField(blank=True, null=True)
#
#
# class Episode(models.Model):
#     season = models.ForeignKey(Season, on_delete=models.CASCADE)
#     const = models.CharField(max_length=150, unique=True)
#     number = models.FloatField(blank=True, null=True)
#     name = models.TextField(blank=True, null=True)
#     release_date = models.CharField(blank=True, null=True, max_length=150)
#     rate_imdb = models.CharField(max_length=150, blank=True, null=True)


class Watchlist(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    added_date = models.DateField()
    set_to_delete = models.BooleanField(default=False)


class Favourite(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.entry.name