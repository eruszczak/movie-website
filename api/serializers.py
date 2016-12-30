from rest_framework import reverse
from rest_framework import serializers

from movie.models import Rating


class RatingListSerializer(serializers.ModelSerializer):
    genre = serializers.SerializerMethodField()
    url = serializers.URLField(source='title.get_absolute_url')
    rate_date_formatted = serializers.SerializerMethodField()
    # reverse

    class Meta:
        model = Rating
        fields = 'url genre rate rate_date rate_date_formatted'.split()

    @staticmethod
    def get_genre(obj):
        return ', '.join([g.name for g in obj.title.genre.all()])

    @staticmethod
    def get_rate_date_formatted(obj):
        return obj.rate_date.strftime('%b %d, %A')
