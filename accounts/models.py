from os.path import join, isfile

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models

from shared.helpers import get_random_file_path
from shared.models import FolderPathMixin
from titles.models import Title, Rating
from importer.constants import EXPORT_FILE_NAME


class User(FolderPathMixin, AbstractUser):
    update_date = models.DateTimeField(auto_now=True)

    picture = models.ImageField(upload_to=get_random_file_path, blank=True, null=True)
    imdb_id = models.CharField(blank=True, max_length=15)
    tagline = models.CharField(blank=True, max_length=100)

    MODEL_FOLDER_NAME = 'accounts'

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail', args=[self.username])

    def edit_url(self):
        return reverse('user-edit')

    def watchlist_url(self):
        return reverse('watchlist-list', args=[self.username])

    def favourite_url(self):
        return reverse('favourite-list', args=[self.username])

    def ratings_url(self):
        return reverse('title-list') + '?user={}'.format(self.pk)

    @property
    def imdb_url(self):
        if self.imdb_id:
            return f'http://www.imdb.com/user/{self.imdb_id}/'
        return ''

    @property
    def imdb_ratings_url(self):
        imdb_url = self.imdb_url
        if imdb_url:
            return f'{imdb_url}ratings/'
        return ''

    @property
    def imdb_watchlist_url(self):
        imdb_url = self.imdb_url
        if imdb_url:
            return f'{imdb_url}watchlist/'
        return ''

    # @property
    # def imdb_ratings_rss_url(self):
    #     if self.imdb_id:
    #         return f'http://www.rss.imdb.com/user/{self.imdb_id}/ratings'
    #     return ''
    #
    # @property
    # def imdb_watchlist_rss_url(self):
    #     if self.imdb_id:
    #         return f'http://www.rss.imdb.com/user/{self.imdb_id}/watchlist'
    #     return ''

    @property
    def exported_ratings_file(self):
        # can use default_storage so I won't need a absolute path
        export_file_path = join(self.get_temp_folder_path(absolute=True), EXPORT_FILE_NAME)
        if isfile(export_file_path):
            return {
                'path': f'/media/{join(self.get_temp_folder_path(), EXPORT_FILE_NAME)}',
                'name': EXPORT_FILE_NAME
            }
        return None

    @property
    def avatar_url(self):
        if self.picture:
            return self.picture.url
        return f'http://api.adorable.io/avatar/200/{self.username}'

    @property
    def latest_rated_title(self):
        latest_rating = Rating.objects.filter(user=self).latest('rate_date')
        if latest_rating:
            return latest_rating.title
        return None

    @property
    def count_ratings(self):
        return Rating.objects.filter(user=self).count()

    @property
    def count_titles(self):
        """counts rated distinct titles"""
        return Title.objects.filter(rating__user=self).distinct().count()


class UserFollow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='follower')
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed')

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return '{} follows {}'.format(self.follower.username, self.followed.username)
