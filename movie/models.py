from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.db import models
from utils.utils import build_datetime_obj
import datetime
import sys


class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def get_absolute_url(self):
        return reverse('entry_show_from_genre', kwargs={'genre': self.name})

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Entry(models.Model):
    genre = models.ManyToManyField(Genre)
    director = models.ManyToManyField(Director)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    const = models.CharField(max_length=30, unique=True)
    name = models.TextField(blank=True, null=True)
    rate = models.IntegerField(blank=True, null=True)
    rate_imdb = models.FloatField(blank=True, null=True)
    rate_date = models.DateField(blank=True, null=True)
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
    slug = models.SlugField(unique=True)
    img = models.ImageField(null=True, blank=True)
    watch_again_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.name, self.year)

    def get_absolute_url(self):
        return reverse('entry_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify('{} {}'.format(self.name, self.year))
        super(Entry, self).save(*args, **kwargs)

    @property
    def yesterday_today_month(self):
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(1)
        rate_date = str(self.rate_date)
        if rate_date == today.strftime('%Y-%m-%d'):
            return 'today'
        elif rate_date == yesterday.strftime('%Y-%m-%d'):
            return 'yesterday'
        elif self.rate_date.strftime('%Y-%m') == today.strftime('%Y-%m'):
            return 'this month'
        return False

    @property
    def timesince_rating(self):
        return '{} days ago'.format((datetime.datetime.now() - build_datetime_obj(self.rate_date)).days)


class Archive(models.Model):
    const = models.CharField(max_length=30, blank=True, null=True)
    rate = models.CharField(max_length=30, blank=True, null=True)
    rate_date = models.DateField(blank=True, null=True)
    watch_again_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.const

    @property
    def days_since_added_to_watchlist(self):
        current_rating_date = self.calculate_next_rating()
        added = build_datetime_obj(self.watch_again_date)
        days_diff = (current_rating_date - added).days
        return days_diff

    @property
    def days_since_previous_rating(self):
        current_rating_date = self.calculate_next_rating()
        archived_rating_date = build_datetime_obj(self.rate_date)
        days_diff = (current_rating_date - archived_rating_date).days
        return days_diff

    @property
    def get_entry(self):
        return get_object_or_404(Entry, const=self.const)

    def calculate_next_rating(self):
        find_objs = None
        called_by = sys._getframe(1).f_code.co_name
        if called_by == 'days_since_added_to_watchlist':
            find_objs = Archive.objects.filter(const=self.const, rate_date__gt=self.watch_again_date)
        elif called_by == 'days_since_previous_rating':
            find_objs = Archive.objects.filter(const=self.const, rate_date__gt=self.rate_date)
        if find_objs:
            obj = find_objs[0].rate_date  # assume [0] is the first possible
            current_date = build_datetime_obj(obj)
        else:
            entry = get_object_or_404(Entry, const=self.const)
            current_date = build_datetime_obj(entry.rate_date)
        return current_date


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
