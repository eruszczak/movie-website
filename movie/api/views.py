import calendar
from datetime import datetime
from collections import OrderedDict
from utils.utils import build_url
from chart.charts import count_for_month_lists

from ..models import Title, Genre
from django.db.models import Q, Count

from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from .pagination import SetPagination
from .serializers import TitleListSerializer, GenreListSerializer, TitleWatchListSerializer


class TitleListView(ListAPIView):
    serializer_class = TitleListSerializer
    pagination_class = SetPagination

    def get_queryset(self):
        queryset = Title.objects.all().order_by('-rate_date')
        query = self.request.GET.get('q')
        year = self.request.GET.get('year')
        genre = self.request.GET.get('genre')
        rated = self.request.GET.get('rated')
        rated_year = self.request.GET.get('rated_year')
        rated_month = self.request.GET.get('rated_month')
        # title = self.request.GET.get('title')
        # if title:
        #     queryset = queryset.filter(name__icontains=title) if len(title) > 2\
        #         else queryset.filter(name__startswith=title)
        if query:
            if len(query) > 2:
                queryset = queryset.filter(Q(name__icontains=query) | Q(year=query)).distinct()
            else:
                queryset = queryset.filter(Q(name__startswith=query) | Q(year=query)).distinct()
        if rated:
            queryset = queryset.filter(rate=rated)
        if year:
            queryset = queryset.filter(year=year)
        if rated_year and rated_month:
            # queryset = queryset.filter(rate_date__year=rated_year),
            queryset = Title.objects.filter(rate_date__year=rated_year, rate_date__month=rated_month)
        if genre:
            queryset = Genre.objects.get(name=genre).entry_set.all()
        return queryset


class TitleDetailView(RetrieveAPIView):
    queryset = Title.objects.all()
    serializer_class = TitleListSerializer
    lookup_field = 'slug'


class GenreListView(ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreListSerializer


class Genre2(ListAPIView):
    # bigger pagination
    def get(self, request, *args, **kwargs):
        abs_url = request.build_absolute_uri(reverse('api-movie:entry_list'))
        genre_count = Genre.objects.values('name').annotate(the_count=Count('entry')).order_by('-the_count')
        for obj in genre_count:
            obj['details'] = build_url(abs_url, get={'genre': obj['name']})
        response = Response(genre_count)
        return response


class RateListView(ListAPIView):
    def get(self, request, *args, **kwargs):
        abs_url = request.build_absolute_uri(reverse('api-movie:entry_list'))
        rate_count = Title.objects.values('rate').annotate(the_count=Count('rate')).order_by('rate')
        for obj in rate_count:
            obj['details'] = build_url(abs_url, get={'rated': obj['rate']})
        response = Response(rate_count)
        return response


class YearListView(ListAPIView):
    def get(self, request, *args, **kwargs):
        abs_url = request.build_absolute_uri(reverse('api-movie:entry_list'))
        year_count = Title.objects.values('year').annotate(the_count=Count('year')).order_by('year')
        for obj in year_count:
            obj['details'] = build_url(abs_url, get={'year': obj['year']})
        response = Response(year_count)
        return response


class MonthListView(ListAPIView):
    def get(self, request, *args, **kwargs):
        abs_url = request.build_absolute_uri(reverse('api-movie:entry_list'))
        d = {}  # OrderedDict()
        # t = {} todo
        for year in range(2014, datetime.now().year + 1):
            count_per_month = count_for_month_lists(year=year)
            # for value, month in count_per_month:
            #     t[month] = {
            #         year: {
            #             'count': value,
            #             'link': build_url(abs_url, get={'rated_year': year, 'rated_month': month}),
            #         },
            #     }
            # print(t[month])
            # print(count_per_month)
            d[year] = OrderedDict(
                (calendar.month_abbr[int(month.lstrip('0'))], {
                    'count': value,
                    'details': build_url(abs_url, get={'rated_year': year, 'rated_month': month}),
                    # 'link': reverse('entry_show_rated_in_month', kwargs={'year': year, 'month': month})
                })
                for value, month in count_per_month
            )
        response = Response(d)  # OrderedDict(reversed(d.items())))
        return response


class WatchAgainUpdateView(UpdateAPIView):
    queryset = Title.objects.all()
    serializer_class = TitleWatchListSerializer
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        return Response(self.get_object().watch_again_date)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.watch_again_date:
            instance.watch_again_date = datetime.now()
        else:
            instance.watch_again_date = None
        instance.save()
        return Response(instance)
