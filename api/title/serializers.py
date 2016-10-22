from movie.models import Title, Genre
from rest_framework import serializers
# from rest_framework.filters import SearchFilter, OrderingFilter


class TitleListSerializer(serializers.ModelSerializer):
    genre = serializers.SerializerMethodField()
    director = serializers.SerializerMethodField()
    url_details = serializers.HyperlinkedIdentityField(view_name='api-title:title_detail', lookup_field='slug')
    url = serializers.HyperlinkedIdentityField(view_name='entry_details', lookup_field='slug')
    # rate_date2 = serializers.SerializerMethodField()
    # detail_page = serializers.URLField(source='get_absolute_url')
    # filter_backends = [SearchFilter, OrderingFilter]        # /?search=, &ordering=-date
    # search_fields = ['title', 'content']                    # different way, built-in search
    class Meta:
        model = Title
        fields = 'name year genre director const url url_details'.split()
        # fields = '__all__'

    def get_genre(self, obj):
        return [g.name for g in obj.genre.all()]

    def get_director(self, obj):
        directors = [d.name for d in obj.director.all()]
        return directors if directors[0] != 'N/A' else None


# class TitleDetailSerializer(serializers.ModelSerializer):
#     # detail_url = serializers.HyperlinkedIdentityField(view_name='entry-api:detail')
#
#     class Meta:
#         model = Title
#         fields = ['name']
#         # fields = '__all__'


class GenreListSerializer(serializers.ModelSerializer):
    the_count = serializers.IntegerField(source='title_set.count')
    # detail_url = serializers.HyperlinkedIdentityField(view_name='api-movie:entry_detail', lookup_field='slug')
    # build url
    url_details = serializers.HyperlinkedIdentityField(view_name='api-title:genre_detail', lookup_field='name', lookup_url_kwarg='genre')
    url = serializers.HyperlinkedIdentityField(view_name='entry_show_from_genre', lookup_field='name', lookup_url_kwarg='genre')

    class Meta:
        model = Genre
        fields = 'name the_count url_details url'.split()


# class GenreDetailSerializer(serializers.ModelSerializer):
#     the_count = serializers.IntegerField(source='title_set.count')
#     # detail_url = serializers.HyperlinkedIdentityField(view_name='api-movie:entry_detail', lookup_field='slug')
#
#     class Meta:
#         model = Genre
#         fields = ['name', 'the_count']

