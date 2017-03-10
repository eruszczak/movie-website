import os
from datetime import datetime

from django.db import models
from django.utils import timezone
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from movie.models import Title
from common.sql_queries import avg_of_user_current_ratings
from mysite.settings import MEDIA_ROOT


def update_filename(instance, filename):
    path = os.path.join("user_files", instance.user.username)
    extension = '.' + filename.split('.')[1]
    fname = datetime.now().strftime("%Y-%m-%d %H-%M-%S") + extension
    return os.path.join(path, fname)


def validate_file_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Only csv files are supported')


# todo
def validate_picture_extension(value):
    if not value.name.endswith('.jpg') or not value.name.endswith('.png'):
        raise ValidationError('Only jpg & png files are supported')


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    picture = models.ImageField(upload_to=update_filename, blank=True, null=True)
    imdb_id = models.CharField(blank=True, null=True, max_length=15)
    csv_ratings = models.FileField(upload_to=update_filename, validators=[validate_file_extension], blank=True, null=True)

    last_updated_csv_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_watchlist = models.DateTimeField(null=True, blank=True)
    last_updated_profile = models.DateTimeField(auto_now=True, null=True, blank=True)

    __original_picture = None
    __original_csv = None

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.__original_picture = self.picture
        self.__original_csv = self.csv_ratings
        self.user_folder = os.path.join(MEDIA_ROOT, 'user_files', self.user.username)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        picture_changed = self.picture != self.__original_picture
        csv_changed = self.csv_ratings != self.__original_csv
        if picture_changed:
            self.delete_previous_file('picture')
        if csv_changed:
            self.delete_previous_file('csv')

        super(UserProfile, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_picture = self.picture
        self.__original_csv = self.csv_ratings

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
    def picture_filename(self):
        return str(self.picture).split('/')[-1] if self.picture else ''

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

    def delete_previous_file(self, what_to_delete):
        for file in os.listdir(self.user_folder):
            if UserProfile.get_extension_condition(file, what_to_delete):
                path = os.path.join(self.user_folder, file)
                os.remove(path)

    @staticmethod
    def get_extension_condition(file, what_to_delete):
        if what_to_delete == 'picture':
            return file.endswith('.jpg') or file.endswith('.png')
        elif what_to_delete == 'csv':
            return file.endswith('.csv')
        return False


class UserFollow(models.Model):
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE)
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_user')

    class Meta:
        unique_together = ('user_follower', 'user_followed')

    def __str__(self):
        return '{} follows {}'.format(self.user_follower.username, self.user_followed.username)
