from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from shared.helpers import get_random_file_path
from shared.models import FolderPathMixin
from titles.models import Title, Rating


class User(FolderPathMixin, AbstractUser):
    picture = models.ImageField(upload_to=get_random_file_path, blank=True, null=True)
    imdb_id = models.CharField(blank=True, max_length=15)
    tagline = models.CharField(blank=True, max_length=100)
    # csv_ratings = models.FileField(upload_to=get_random_file_path, validators=[validate_file_ext], blank=True)

    last_updated_csv_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_ratings = models.DateTimeField(null=True, blank=True)
    last_updated_rss_watchlist = models.DateTimeField(null=True, blank=True)
    last_updated_profile = models.DateTimeField(auto_now=True, null=True, blank=True)

    MODEL_FOLDER_NAME = 'accounts'

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
    def count_titles(self):
        """counts rated distinct titles"""
        return Title.objects.filter(rating__user=self).distinct().count()

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
        if time:
            return (timezone.now() - time).seconds > 180
        return False

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
