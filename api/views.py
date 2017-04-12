from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models.functions import ExtractMonth, ExtractYear

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from movie.models import Rating, Title
from .serializers import RatingListSerializer, TitleSerializer
from common.sql_queries import rating_distribution


from rest_framework.pagination import PageNumberPagination


class SetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'per_page'


class RatingsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingListSerializer
    pagination_class = SetPagination  # by default, only ViewSets can use per_page parameter


    def get_queryset(self):
        if self.request.GET.get('u'):
            self.queryset = Rating.objects.filter(user__username=self.request.GET['u'])
        return self.queryset


# class TitleListView(ListAPIView):
#     queryset = Title.objects.all()
#     serializer_class = TitleSerializer
#     pagination_class = SetPagination


class TitleDetailView(RetrieveAPIView):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    lookup_field = 'slug'


class Genres(ListAPIView):
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('u')
        if username is not None:
            genre_count = Title.objects.filter(rating__user__username=username).values('genre__name')\
                .annotate(the_count=Count('pk', distinct=True)).filter(genre__name__isnull=False).order_by('the_count')
            return Response(genre_count)

        genre_count = Title.objects.all().values('genre__name')\
            .annotate(the_count=Count('pk', distinct=True)).filter(genre__name__isnull=False).order_by('the_count')
        return Response(genre_count)


class Years(ListAPIView):
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('u')
        if username is not None:
            year_count = Title.objects.filter(rating__user__username=username).values('year')\
                .annotate(the_count=Count('pk', distinct=True)).order_by('year')
            return Response(year_count)

        year_count = Title.objects.all().values('year').annotate(the_count=Count('pk')).order_by('year')
        return Response(year_count)


class Rates(ListAPIView):
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('u')
        if username is not None:
            user = get_object_or_404(User, username=username)
            data = {'data_rates': rating_distribution(user.id)}
            return Response(data)

        return Response(status=status.HTTP_204_NO_CONTENT)


class MonthlyRatings(ListAPIView):
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('u')
        if username is not None:
            count_per_months = Rating.objects.filter(user__username=username)\
                .annotate(month=ExtractMonth('rate_date'), year=ExtractYear('rate_date'))\
                .values('month', 'year').order_by('year', 'month')\
                .annotate(the_count=Count('title'))
            return Response(count_per_months)

        return Response(status=status.HTTP_204_NO_CONTENT)
