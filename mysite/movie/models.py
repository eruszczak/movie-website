from django.db import models


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
    name = models.CharField(max_length=150)
    rate = models.CharField(max_length=30)
    rate_imdb = models.CharField(max_length=30)
    rate_date = models.CharField(blank=True, null=True)
    runtime = models.CharField(max_length=30)
    year = models.CharField(max_length=30)
    release_date = models.CharField(blank=True, null=True)
    votes = models.CharField(max_length=30)
    url_imdb = models.URLField(blank=True, null=True)
