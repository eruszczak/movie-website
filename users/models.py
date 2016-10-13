from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    imdb_id = models.CharField(blank=True, null=True, max_length=15)
    imdb_ratings = models.FileField(upload_to='user_imdb_ratings', blank=True, null=True)
    imdb_ratings_used = models.DateTimeField(null=True, blank=True)
    picture = models.ImageField(upload_to='user_avatars', blank=True, null=True)
    ratings_last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username