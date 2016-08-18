from ..models import Entry, Genre
from rest_framework import serializers
# from rest_framework.filters import SearchFilter, OrderingFilter


class EntryListSerializer(serializers.ModelSerializer):
    genre = serializers.SerializerMethodField()
    director = serializers.SerializerMethodField()
    detail_page = serializers.URLField(source='get_absolute_url')
    detail_url = serializers.HyperlinkedIdentityField(view_name='api-movie:entry_detail', lookup_field='slug')
    # detail_url = serializers.HyperlinkedIdentityField(view_name='comments-api:thread')
    # filter_backends = [SearchFilter, OrderingFilter]        # /?search=, &ordering=-date
    # search_fields = ['title', 'content']                    # different way, built-in search
    class Meta:
        model = Entry
        fields = 'name year genre director detail_page detail_url'.split()
        # fields = '__all__'

    def get_genre(self, obj):
        return [g.name for g in obj.genre.all()]

    def get_director(self, obj):
        directors = [d.name for d in obj.director.all()]
        return directors if directors[0] != 'N/A' else None


class EntryDetailSerializer(serializers.ModelSerializer):
    # detail_url = serializers.HyperlinkedIdentityField(view_name='entry-api:detail')

    class Meta:
        model = Entry
        fields = ['name']
        # fields = '__all__'


class GenreListSerializer(serializers.ModelSerializer):
    the_count = serializers.IntegerField(source='entry_set.count')
    # build url

    class Meta:
        model = Genre
        fields = ['name', 'the_count']


# class RateListSerializer(serializers.Serializer):
#     rate_count = serializers.DictField()

    # class Meta:
    #     fields = ['name']
    #     # fields = '__all__'

    # def get_rate_count(self, obj):
    #     rate_count = Entry.objects.values('rate').annotate(the_count=Count('rate')).order_by('rate')
    #     return rate_count