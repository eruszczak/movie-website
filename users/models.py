import os
from datetime import datetime

from django.db import models
from django.utils import timezone
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from recommend.models import Recommendation
from movie.models import Title
from common.sql_queries import avg_of_user_current_ratings


def update_filename(instance, filename):
    path = os.path.join("user_files", instance.user.username)
    extension = '.' + filename.split('.')[1]
    fname = datetime.now().strftime("%Y-%m-%d %H-%M-%S") + extension
    return os.path.join(path, fname)


def validate_file_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Only csv files are supported')


# class UserQuerySet(models.QuerySet):
#     def authors(self):
#         pass


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    picture = models.ImageField(upload_to=update_filename, blank=True, null=True)
    imdb_id = models.CharField(blank=True, null=True, max_length=15)
    csv_ratings = models.FileField(upload_to=update_filename, validators=[validate_file_extension], blank=True, null=True)

    last_updated_csv_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_watchlist = models.DateTimeField(null=True, blank=True)
    last_updated_profile = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('user_profile', kwargs={'username': self.user.username})

    def watchlist_url(self):
        return reverse('watchlist', kwargs={'username': self.user.username})

    def favourite_url(self):
        return reverse('favourite', kwargs={'username': self.user.username})

    def recommend_url(self):
        return reverse('recommend', kwargs={'username': self.user.username})

    def ratings_url(self):
        return reverse('explore') + '?u={}'.format(self.user.username)

    def ratings_exclude(self):
        return reverse('explore') + '?u={}&exclude_mine=on'.format(self.user.username)

    @property
    def count_ratings(self):
        return Title.objects.filter(rating__user=self.user).distinct().count()

    @property
    def avg_of_current_ratings(self):
        return avg_of_user_current_ratings(self.id)

    @property
    def can_update_csv_ratings(self):
        return self.have_minutes_passed(self.last_updated_csv_ratings)

    @property
    def can_update_rss_ratings(self):
        return self.have_minutes_passed(self.last_updated_rss_ratings)

    @property
    def can_update_rss_watchlist(self):
        return self.have_minutes_passed(self.last_updated_rss_watchlist)

    @staticmethod
    def have_minutes_passed(time):
        if not time:
            return True
        return (timezone.now() - time).seconds > 60 * 3


class UserFollow(models.Model):
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE)
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_user')

    class Meta:
        unique_together = ('user_follower', 'user_followed')

    def __str__(self):
        return '{} follows {}'.format(self.user_follower.username, self.user_followed.username)
