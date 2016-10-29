from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.db import models
from datetime import datetime
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

    const = models.CharField(unique=True, max_length=9)
    name = models.TextField()

    rate_imdb = models.FloatField(blank=True, null=True)
    runtime = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    votes = models.IntegerField(blank=True, null=True)

    url_poster = models.URLField(blank=True, null=True, max_length=200)
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
    img = models.ImageField(upload_to='poster', null=True, blank=True)
    watch_again_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ('-rating__rate_date', '-inserted_date')

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
    rate = models.IntegerField()
    rate_date = models.DateField()

    class Meta:
        unique_together = ('user', 'title', 'rate', 'rate_date')
        ordering = ('-rate_date', )

    def __str__(self):
        return '{} {}'.format(self.title.name, self.rate_date)

    # rating manager -> Watchlist.objects.current rating for user
    @property
    def current_rating(self):
        return Rating.objects.filter(user=self.user).filter(title=self.title).first()

    @property
    def next_rating_days_diff(self):
        next_rating = Rating.objects.filter(user=self.user).filter(title=self.title, rate_date__gt=self.rate_date).last()
        if next_rating:
            return (next_rating.rate_date - self.rate_date).days
        return (datetime.now().date() - self.rate_date).days


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    added_date = models.DateTimeField(default=timezone.now)
    imdb = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-added_date', )
        unique_together = ('user', 'title', 'added_date', 'imdb')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.title.year)

    @property
    def is_rated_with_later_date(self):
        return Rating.objects.filter(user=self.user).filter(title=self.title, rate_date__gt=self.added_date).exists()  # , title__watchlist__imdb=True

    # in view send property above and in template use property below
    @property
    def rated_after_days_diff(self):
        rating = Rating.objects.filter(user=self.user).filter(title=self.title, rate_date__gt=self.added_date).last()
        if rating:
            return rating.rate_date - self.added_date


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    added_date = models.DateTimeField(default=timezone.now)
    order = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.title.name, self.title.year)

    class Meta:
        ordering = ('order', )
