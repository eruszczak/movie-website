from rest_framework import reverse
from rest_framework import serializers

from titles.models import Rating, Title


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SerializerMethodField()
    director = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    @staticmethod
    def get_genre(obj):
        return [g.name for g in obj.genre.all()]

    @staticmethod
    def get_actor(obj):
        return [a.name for a in obj.actor.all()]

    @staticmethod
    def get_director(obj):
        directors = [d.name for d in obj.director.all()]
        return directors if directors[0] != 'N/A' else None


class TitlePreviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Title
        fields = ['name', 'year']


class RatingListSerializer(serializers.HyperlinkedModelSerializer ):
    url = serializers.URLField(source='title.get_absolute_url')
    rate_date_formatted = serializers.SerializerMethodField()

    # title = TitlePreviewSerializer()
    title = TitleSerializer()  # this works better than depth
    # detail_url = serializers.HyperlinkedIdentityField(many=True, view_name='title_detail', lookup_field='slug', read_only=True)

    class Meta:
        model = Rating
        fields = ['rate_date_formatted', 'rate', 'rate_date', 'url', 'title']
        # depth = 1  # attaches related models

    @staticmethod
    def get_rate_date_formatted(obj):
        return obj.rate_date.strftime('%b %d, %A')


