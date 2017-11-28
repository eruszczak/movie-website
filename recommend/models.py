from django.conf import settings
from django.db import models
from titles.models import Title, Rating
from django.utils import timezone


class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    added_date = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='sender_user'
    )
    nick = models.CharField(blank=True, null=True, max_length=30)
    note = models.CharField(blank=True, null=True, max_length=120)

    class Meta:
        ordering = ('-added_date', )
        unique_together = ('user', 'title')

    def __str__(self):
        return '{} recommended "{}" to {}'.format(
            self.sender.username if self.sender else self.nick,
            self.title.name[:10],
            self.user.username
        )

    @property
    def is_active(self):
        return not Rating.objects.filter(user=self.user, title=self.title, rate_date__gte=self.added_date).exists()
