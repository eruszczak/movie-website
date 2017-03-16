from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models.functions import ExtractMonth, ExtractYear

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from movie.models import Rating, Title
from .serializers import RatingListSerializer
from common.sql_queries import rating_distribution


class RatingsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingListSerializer

    def get_queryset(self):
        #.order_by('-rate_date')
        # query = self.request.GET.get('q')
        # year = self.request.GET.get('year')
        # genre = self.request.GET.get('genre')
        # user = self.request.GET.get('user')
        #
        # # rated = self.request.GET.get('rated')
        # # rated_year = self.request.GET.get('rated_year')
        # # rated_month = self.request.GET.get('rated_month')
        # # title = self.request.GET.get('title')
        # # if title:
        # #     queryset = queryset.filter(name__icontains=title) if len(title) > 2\
        # #         else queryset.filter(name__startswith=title)
        # if query:
        #     # if len(query) > 2:
        #     #     queryset = queryset.filter(Q(name__icontains=query) | Q(year=query)).distinct()
        #     # else:
        #     #     queryset = queryset.filter(Q(name__startswith=query) | Q(year=query)).distinct()
        #     queryset = queryset.filter(Q(name__icontains=query) | Q(year=query)).distinct() if len(query) > 2\
        #         else queryset.filter(Q(name__startswith=query) | Q(year=query)).distinct()
        # # if rated:
        # #     queryset = queryset.filter(rate=rated)
        # if year:
        #     queryset = queryset.filter(year=year)
        # # if rated_year and rated_month:
        #     # queryset = queryset.filter(rate_date__year=rated_year),
        #     # queryset = Title.objects.filter(rate_date__year=rated_year, rate_date__month=rated_month)
        # if genre:
        #     queryset = Genre.objects.get(name=genre).entry_set.all()
        return self.queryset


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
            count_per_months = Rating.objects.annotate(month=ExtractMonth('rate_date'), year=ExtractYear('rate_date'))\
                .values('month', 'year').order_by('year', 'month')\
                .annotate(the_count=Count('title', distinct=True))
            return Response(count_per_months)
        return Response(status=status.HTTP_204_NO_CONTENT)
