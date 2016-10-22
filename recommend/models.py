from django.db import models
from movie.models import Title
from django.contrib.auth.models import User
from django.utils import timezone

# class Recommendation(models.Model):
#     const = models.CharField('title', max_length=50, unique=True)
#     nick = models.CharField(max_length=30)
#     note = models.CharField(blank=True, null=True, max_length=120)
#     name = models.TextField(blank=True, null=True)
#     year = models.CharField(blank=True, null=True, max_length=5)
#     date = models.DateField(auto_now=False, auto_now_add=True)
#     date_insert = models.DateTimeField(auto_now=False, auto_now_add=True)
#     is_rated = models.BooleanField(default=False)


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    added_date = models.DateTimeField(default=timezone.now)
    nick = models.CharField(blank=True, null=True, max_length=30)
    note = models.CharField(blank=True, null=True, max_length=120)

    class Meta:
        ordering = ('-added_date', )
