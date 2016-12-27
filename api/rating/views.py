from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from movie.models import Rating, Title
from .pagination import SetPagination
from .serializers import RatingListSerializer


class RatingListView(ListAPIView):
    serializer_class = RatingListSerializer
    pagination_class = SetPagination

    def get_queryset(self):
        queryset = Rating.objects.all()#.order_by('-rate_date')
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
        return queryset


class Genres(ListAPIView):
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('u')
        if username is not None:
            genre_count = Title.objects.filter(rating__user__username=username)\
                .values('genre__name').annotate(the_count=Count('genre')).order_by('genre')
            return Response(genre_count)
        return Response()


class Years(ListAPIView):
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('u')
        if username is not None:
            year_count = Title.objects.filter(rating__user__username=username) \
                .values('year').annotate(the_count=Count('year')).order_by('year')
            return Response(year_count)
        return Response()


class Rates(ListAPIView):
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('u')
        if username is not None:
            rate_count = Rating.objects.filter(user__username=username) \
                .values('rate').annotate(the_count=Count('rate')).order_by('rate')
            return Response(rate_count)
        return Response()


class MonthlyRatings(ListAPIView):
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('u')
        if username is not None:
            count_per_months = Rating.objects.annotate(month=ExtractMonth('rate_date'), year=ExtractYear('rate_date'))\
                .values('month', 'year').distinct().order_by('year', 'month')\
                .annotate(the_count=Count('id'))
            return Response(count_per_months)
        return Response()
