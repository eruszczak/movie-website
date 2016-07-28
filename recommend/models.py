from django.db import models


class Recommendation(models.Model):
    const = models.CharField('title', max_length=50, unique=True)
    nick = models.CharField(max_length=30)
    note = models.CharField(blank=True, null=True, max_length=120)
    name = models.TextField(blank=True, null=True)
    year = models.CharField(blank=True, null=True, max_length=5)
    date = models.DateField(auto_now=False, auto_now_add=True)
    date_insert = models.DateTimeField(auto_now=False, auto_now_add=True)
    is_rated = models.BooleanField(default=False)
