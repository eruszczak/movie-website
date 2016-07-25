from django.db import models


class Recommendation(models.Model):
    const = models.CharField('IMDb URL or ID', max_length=50, unique=True)
    nick = models.CharField(max_length=30)
    note = models.CharField(blank=True, null=True, max_length=120)
    name = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now=False, auto_now_add=True)


