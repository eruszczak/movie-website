from movie.models import Rating
from rest_framework import serializers
# from rest_framework.filters import SearchFilter, OrderingFilter


class RatingListSerializer(serializers.ModelSerializer):
    user = serializers.RelatedField(read_only=True)
    # genre = serializers.SerializerMethodField()
    # director = serializers.SerializerMethodField()
    # url_details = serializers.HyperlinkedIdentityField(view_name='api-title:title_detail', lookup_field='slug')
    # url = serializers.HyperlinkedIdentityField(view_name='entry_details', lookup_field='slug')
    # rate_date2 = serializers.SerializerMethodField()
    # detail_page = serializers.URLField(source='get_absolute_url')
    # filter_backends = [SearchFilter, OrderingFilter]        # /?search=, &ordering=-date
    # search_fields = ['title', 'content']                    # different way, built-in search
    class Meta:
        model = Rating
        fields = 'rate rate_date user'.split()
        # fields = '__all__'

    # def get_genre(self, obj):
    #     return [g.name for g in obj.genre.all()]
    #
    # def get_director(self, obj):
    #     directors = [d.name for d in obj.director.all()]
    #     return directors if directors[0] != 'N/A' else None
