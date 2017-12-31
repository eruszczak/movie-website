from django.contrib.auth import get_user_model
from rest_framework import serializers

from titles.models import Rating, Title, Person, Genre

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ['name']


class TitleSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    year = serializers.ReadOnlyField()
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    poster_small = serializers.ReadOnlyField()
    poster_backdrop_title = serializers.ReadOnlyField()
    imdb_url = serializers.ReadOnlyField()
    release_date = serializers.ReadOnlyField()

    class Meta:
        model = Title
        fields = ('year', 'name', 'url', 'type', 'poster_small', 'release_date', 'poster_backdrop_title', 'overview', 'genres', 'imdb_url')

    @staticmethod
    def get_type(obj):
        return obj.get_type_display()

    @staticmethod
    def get_url(obj):
        return obj.get_absolute_url()


class TitlePreviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = ['name', 'year']


class RatingListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.URLField(source='title.get_absolute_url')
    rate_date_formatted = serializers.SerializerMethodField()

    # title = TitlePreviewSerializer()
    title = TitleSerializer()  # this works better than depth

    class Meta:
        model = Rating
        fields = ['rate_date_formatted', 'rate', 'rate_date', 'url', 'title']
        # depth = 1  # attaches related models

    @staticmethod
    def get_rate_date_formatted(obj):
        return obj.rate_date.strftime('%b %d, %A')


class PersonSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ('name', 'url', 'img',)

    @staticmethod
    def get_url(obj):
        return obj.get_absolute_url()

    @staticmethod
    def get_img(obj):
        return obj.picture