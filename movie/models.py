from django.core.urlresolvers import reverse
from django.utils import timezone
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from .utils.functions import create_slug
from common.sql_queries import avg_of_title_current_ratings


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('explore') + '?g={}'.format(self.name)

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def get_absolute_url(self):
        return reverse('explore') + '?d={}'.format(self.id)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def get_absolute_url(self):
        return reverse('explore') + '?a={}'.format(self.id)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('explore') + '?t={}'.format(self.name)   # todo

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
    img_thumbnail = models.ImageField(null=True, blank=True)

    class Meta:
        ordering = ('-inserted_date', )

    def __str__(self):
        return '{} {}'.format(self.name, self.year)

    def get_absolute_url(self):
        return reverse('title_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = create_slug(self)
        if not self.url_imdb:
            self.url_imdb = 'http://www.imdb.com/title/{}/'.format(self.const)
        super(Title, self).save(*args, **kwargs)

    @property
    def rate(self):
        return avg_of_title_current_ratings(self.id)  # dict in this form: {count: 20, avg: 7.0}

    @property
    def can_be_updated(self):
        return (timezone.now() - self.last_updated).seconds > 60 * 10


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    rate = models.IntegerField()
    rate_date = models.DateField()
    inserted_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'title', 'rate_date')
        ordering = ('-rate_date', '-inserted_date')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.rate_date)

    def save(self, *args, **kwargs):
        in_watchlist = Watchlist.objects.filter(user=self.user, title=self.title,
                                                added_date__date__lte=self.rate_date, deleted=False).first()
        if in_watchlist:
            if in_watchlist.imdb:
                in_watchlist.deleted = True
                in_watchlist.save(update_fields=['deleted'])
            else:
                in_watchlist.delete()
        super(Rating, self).save(*args, **kwargs)

    @property
    def is_current_rating(self):
        return self == Rating.objects.filter(user=self.user, title=self.title).first()

    @property
    def next_rating_days_diff(self):
        next_rating = Rating.objects.filter(user=self.user, title=self.title, rate_date__gt=self.rate_date).last()
        if next_rating:
            return (next_rating.rate_date - self.rate_date).days
        return (datetime.now().date() - self.rate_date).days

    def rated_before_rate_diff(self):
        previous = Rating.objects.filter(user=self.user, title=self.title, rate_date__lt=self.rate_date).first()
        if previous:
            return self.rate - previous.rate
        return None


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
        unique_together = ('user', 'title')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.title.year)

    def save(self, *args, **kwargs):
        if not self.id and self.imdb:
            # if there's later rating then it's not "active" anymore and should be deleted
            rated_later = Rating.objects.filter(user=self.user, title=self.title, rate_date__gte=self.added_date.date())
            if rated_later.exists():
                self.deleted = True
        super(Watchlist, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('watchlist', kwargs={'username': self.user.username})

    # todo
    @property
    def rated_after_days_diff(self):
        rating = Rating.objects.filter(user=self.user).filter(title=self.title, rate_date__gt=self.added_date).last()
        if rating:
            return {
                'rate': rating.rate,
                'days_diff': (rating.rate_date - self.added_date.date()).days
            }
        return None


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    added_date = models.DateTimeField(default=timezone.now)
    order = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ('order', )
        unique_together = ('user', 'title')

    def __str__(self):
        return '{} {}'.format(self.title.name, self.title.year)

    def get_absolute_url(self):
        return reverse('favourite', kwargs={'username': self.user.username})
