from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=30)

class Director(models.Model):
    name = models.CharField(max_length=150)

class Type(models.Model):
    name = models.CharField(max_length=30)

class Entry(models.Model):
    genre = models.ManyToManyField(Genre)
    director = models.ManyToManyField(Director)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    const = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    rate = models.CharField(max_length=30)
    rate_imdb = models.CharField(max_length=30)
    runtime = models.CharField(max_length=30)
    year = models.CharField(max_length=30)
    votes = models.CharField(max_length=30)
