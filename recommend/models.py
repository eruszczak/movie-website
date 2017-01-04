from django.db import models
from movie.models import Title, Rating
from django.contrib.auth.models import User
from django.utils import timezone


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    added_date = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='sender_user')
    nick = models.CharField(blank=True, null=True, max_length=30)
    note = models.CharField(blank=True, null=True, max_length=120)

    class Meta:
        ordering = ('-added_date', )
        unique_together = ('user', 'title')

    def __str__(self):
        return '{} followed "{}" to {}'.format(self.sender.username if self.sender else self.nick,
                                               self.title.name[:10],
                                               self.user.username)

    @property
    def is_active(self):
        return not Rating.objects.filter(user=self.user, title=self.title, rate_date__gte=self.added_date).exists()
