from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from common.sql_queries import avg_of_user_current_ratings
from shared.helpers import get_random_file_path, validate_file_ext
from shared.models import FolderPathMixin
from titles.constants import MOVIE, SERIES
from titles.models import Title, Rating


class User(FolderPathMixin, AbstractUser):
    picture = models.ImageField(upload_to=get_random_file_path, blank=True, null=True)
    imdb_id = models.CharField(blank=True, null=True, max_length=15)
    tagline = models.CharField(blank=True, null=True, max_length=100)
    csv_ratings = models.FileField(upload_to=get_random_file_path, validators=[validate_file_ext], blank=True, null=True)

    last_updated_csv_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_watchlist = models.DateTimeField(null=True, blank=True)
    last_updated_profile = models.DateTimeField(auto_now=True, null=True, blank=True)

    MODEL_FOLDER_NAME = 'accounts'

    # __original_picture = None
    # __original_csv = None
    #
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     self.__original_picture = self.picture
    #     self.__original_csv = self.csv_ratings

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail', args=[self.username])

    def edit_url(self):
        return reverse('user-edit', args=[self.username])

    def watchlist_url(self):
        return reverse('watchlist', args=[self.username])

    def favourite_url(self):
        return reverse('favourite', args=[self.username])

    def recommend_url(self):
        return reverse('recommend', args=[self.username])

    def ratings_url(self):
        return reverse('title-list') + '?user={}'.format(self.pk)

    def all_ratings_url(self):
        return reverse('title-list') + '?u={}'.format(self.username) + '&all_ratings=on'

    def ratings_exclude(self):
        return reverse('title-list') + '?u={}&exclude_mine=on'.format(self.username)

    @property
    def poster_of_latest_rating(self):
        return Rating.objects.filter(user=self).latest('rate_date').title.poster_backdrop_user

    @property
    def picture_filename(self):
        return str(self.picture).split('/')[-1] if self.picture else ''

    @property
    def count_titles(self):
        """counts rated distinct titles"""
        return Title.objects.filter(rating__user=self).distinct().count()

    @property
    def count_ratings(self):
        """counts all the ratings"""
        return Title.objects.filter(rating__user=self).count()

    @property
    def count_movies(self):
        """counts rated distinct movies"""
        return Title.objects.filter(rating__user=self, type=MOVIE).distinct().count()

    @property
    def count_series(self):
        """counts rated distinct series"""
        return Title.objects.filter(rating__user=self, type=SERIES).distinct().count()

    # TODO
    @property
    def avg_of_current_ratings(self):
        """returns for a user average of his current ratings eg. {avg: 6.40, count: 1942}"""
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

    @staticmethod
    def get_extension_condition(file, what_to_delete):
        if what_to_delete == 'picture':
            return any(file.endswith(ext) for ext in ['.jpg', '.png'])
        elif what_to_delete == 'csv':
            return file.endswith('.csv')
        return False


class UserFollow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='follower')
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed')

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return '{} follows {}'.format(self.follower.username, self.followed.username)
