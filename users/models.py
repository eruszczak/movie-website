import os
from datetime import datetime

from django.db import models

from django.utils import timezone
from django.forms import ValidationError
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse

from title.models import Title
from common.sql_queries import avg_of_user_current_ratings
from mysite.settings import MEDIA_ROOT


def update_filename(instance, file_name):
    path = os.path.join('user_files', instance.user.username)
    extension = '.' + file_name.split('.')[1]
    new_file_name = datetime.now().strftime('%Y-%m-%d %H-%M-%S') + extension
    return os.path.join(path, new_file_name)


def validate_file_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Only csv files are supported')


class User(AbstractUser):
    picture = models.ImageField(upload_to=update_filename, blank=True, null=True)
    imdb_id = models.CharField(blank=True, null=True, max_length=15)
    tagline = models.CharField(blank=True, null=True, max_length=100)
    csv_ratings = models.FileField(upload_to=update_filename, validators=[validate_file_extension], blank=True, null=True)

    last_updated_csv_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_watchlist = models.DateTimeField(null=True, blank=True)
    last_updated_profile = models.DateTimeField(auto_now=True, null=True, blank=True)

    __original_picture = None
    __original_csv = None

    def save(self, *args, **kwargs):
        self.create_user_folder()
        self.clean_user_files()

        super().save(*args, **kwargs)

        self.__original_picture = self.picture
        self.__original_csv = self.csv_ratings

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'username': self.username})

    def edit_url(self):
        return reverse('user-edit', kwargs={'username': self.username})

    def watchlist_url(self):
        return reverse('watchlist', kwargs={'username': self.username})

    def favourite_url(self):
        return reverse('favourite', kwargs={'username': self.username})

    def recommend_url(self):
        return reverse('recommend', kwargs={'username': self.username})

    def ratings_url(self):
        return reverse('title-list') + '?u={}'.format(self.username)

    def all_ratings_url(self):
        return reverse('title-list') + '?u={}'.format(self.username) + '&all_ratings=on'

    def ratings_exclude(self):
        return reverse('title-list') + '?u={}&exclude_mine=on'.format(self.username)

    @property
    def picture_filename(self):
        return str(self.picture).split('/')[-1] if self.picture else ''

    @property
    def count_titles(self):
        """
        counts rated distinct titles
        """
        return Title.objects.filter(rating__user=self).distinct().count()

    @property
    def count_ratings(self):
        """
        counts all the ratings
        """
        return Title.objects.filter(rating__user=self).count()

    @property
    def count_movies(self):
        """
        counts rated distinct m
        """
        return Title.objects.filter(rating__user=self, type__name='movie').distinct().count()

    @property
    def count_series(self):
        """
        counts rated distinct series
        """
        return Title.objects.filter(rating__user=self, type__name='series').distinct().count()

    # TODO
    @property
    def avg_of_current_ratings(self):
        """
        returns for a user average of his current ratings eg. {avg: 6.40, count: 1942}
        """
        return avg_of_user_current_ratings(self.pk)

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
        three_minutes = 3 * 60
        if not time:
            # time is empty if user never did update
            return True
        return (timezone.now() - time).seconds > three_minutes

    def delete_previous_file(self, what_to_delete):
        """
        if user in his settigns uploads new avatar/ratings.csv or replaces it, previous file is deleted
        """
        user_folder = os.path.join(MEDIA_ROOT, 'user_files', self.username)
        for file in os.listdir(user_folder):
            if self.get_extension_condition(file, what_to_delete):
                path = os.path.join(user_folder, file)
                os.remove(path)

    def create_user_folder(self):
        """
        if user doesn't have a folder for his files (avatar and csv) - create it
        """
        directory = os.path.join(MEDIA_ROOT, 'user_files', self.user.username)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def clean_user_files(self):
        """
        when user uploads new avatar or csv, delete previous files because they won't be used anymore
        """
        picture_changed = self.picture != self.__original_picture
        csv_changed = self.csv_ratings != self.__original_csv
        if picture_changed:
            self.delete_previous_file('picture')
        if csv_changed:
            self.delete_previous_file('csv')

    @staticmethod
    def get_extension_condition(file, what_to_delete):
        if what_to_delete == 'picture':
            return any(file.endswith(ext) for ext in ['.jpg', '.png'])
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
