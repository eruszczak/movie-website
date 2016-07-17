from django.db import models
from django.utils import timezone


class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Director(models.Model):
    name = models.CharField(max_length=150, unique=True)


class Type(models.Model):
    name = models.CharField(max_length=30, unique=True)


class Entry(models.Model):
    genre = models.ManyToManyField(Genre)
    director = models.ManyToManyField(Director)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    const = models.CharField(max_length=30, unique=True)
    name = models.TextField(blank=True, null=True)
    rate = models.CharField(max_length=30, blank=True, null=True)
    rate_imdb = models.CharField(max_length=30, blank=True, null=True)
    rate_date = models.CharField(blank=True, null=True, max_length=30)
    runtime = models.CharField(max_length=30, blank=True, null=True)
    year = models.CharField(max_length=30, blank=True, null=True)
    release_date = models.CharField(blank=True, null=True, max_length=30)
    votes = models.CharField(max_length=30, blank=True, null=True)
    url_imdb = models.URLField(blank=True, null=True)
    url_poster = models.URLField(blank=True, null=True)
    url_tomato = models.URLField(blank=True, null=True)
    tomato_user_meter = models.CharField(max_length=30, blank=True, null=True)
    tomato_user_rate = models.CharField(max_length=30, blank=True, null=True)
    tomato_user_reviews = models.CharField(max_length=30, blank=True, null=True)
    tomatoConsensus = models.TextField(blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    inserted_by_updater = models.BooleanField(default=False)
    inserted_date = models.DateTimeField(default=timezone.now, blank=True)


class Archive(models.Model):
    const = models.CharField(max_length=30, blank=True, null=True)
    rate = models.CharField(max_length=30, blank=True, null=True)
    rate_date = models.CharField(blank=True, null=True, max_length=30)


class Season(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    number = models.IntegerField(blank=True, null=True)


class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    const = models.CharField(max_length=30, unique=True)
    number = models.FloatField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    release_date = models.CharField(blank=True, null=True, max_length=30)
    rate_imdb = models.CharField(max_length=30, blank=True, null=True)


class Log(models.Model):
    date = models.DateTimeField(default=timezone.now, blank=True)
    new_inserted = models.IntegerField(blank=True, null=True, default=0)
    updated_archived = models.IntegerField(blank=True, null=True, default=0)
