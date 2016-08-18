import calendar
from collections import OrderedDict
from chart.charts import count_for_month_lists
from datetime import datetime

from django.db.models import Q, Count

from .serializers import EntryListSerializer, GenreListSerializer#, RateListSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from ..models import Entry, Genre
from .pagination import SetPagination
# from django.shortcuts import get_object_or_404    in kwargs i can get details
from rest_framework.reverse import reverse
from utils.utils import build_url


class EntryListView(ListAPIView):
    serializer_class = EntryListSerializer
    # queryset = Entry.objects.all()
    pagination_class = SetPagination    # http://127.0.0.1:8000/api/?per_page=10

    def get_queryset(self):
        queryset = Entry.objects.all()
        year = self.request.GET.get('year')
        query = self.request.GET.get('q')
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
            queryset = Entry.objects.filter(rate_date__year=rated_year, rate_date__month=rated_month)
        return queryset


class EntryDetailView(RetrieveAPIView):
    queryset = Entry.objects.all()
    serializer_class = EntryListSerializer
    lookup_field = 'slug'
    # print(self.kwargs)


class GenreListView(ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreListSerializer


class RateListView(ListAPIView):
    # no serializer because rate don't have a model unlike genre
    def get(self, request, *args, **kwargs):
        abs_url = request.build_absolute_uri(reverse('api-movie:entry_list'))
        rate_count = Entry.objects.values('rate').annotate(the_count=Count('rate')).order_by('rate')
        for obj in rate_count:
            obj['details'] = build_url(abs_url, get={'rated': obj['rate']})
        response = Response(rate_count)
        return response


class YearListView(ListAPIView):
    def get(self, request, *args, **kwargs):
        abs_url = request.build_absolute_uri(reverse('api-movie:entry_list'))
        year_count = Entry.objects.values('year').annotate(the_count=Count('year')).order_by('year')
        for obj in year_count:
            obj['details'] = build_url(abs_url, get={'year': obj['year']})
        response = Response(year_count)
        return response


class MonthListView(ListAPIView):
    # links for details
    # choose year (ratings since 2013, default current year or last)
    def get(self, request, *args, **kwargs):
        abs_url = request.build_absolute_uri(reverse('api-movie:entry_list'))
        d = {}
        for i in range(2014, datetime.now().year + 1):
            count_per_month = count_for_month_lists(year=i)
            d[i] = OrderedDict(
                (calendar.month_abbr[int(month.lstrip('0'))], {
                    'count': value,
                    'link': build_url(abs_url, get={'rated_year': i, 'rated_month': month})})
                for value, month in count_per_month
            )
        response = Response(d)
        return response
