from django.db.models import Q, Count
from .serializers import EntryListSerializer, GenreListSerializer#, RateListSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from ..models import Entry, Genre
from .pagination import SetPagination
from django.shortcuts import get_object_or_404
from rest_framework.reverse import reverse
from utils.utils import build_url

class EntryListView(ListAPIView):
    serializer_class = EntryListSerializer
    # queryset = Entry.objects.all()
    pagination_class = SetPagination    # http://127.0.0.1:8000/api/?per_page=10

    def get_queryset(self):
        queryset = Entry.objects.all()
        year = self.request.GET.get('year')
        title = self.request.GET.get('title')
        query = self.request.GET.get('q')
        rate = self.request.GET.get('rate')
        genre = self.request.GET.get('genre')
        rated = self.request.GET.get('rated')
        # if year:
        #     queryset = queryset.filter(year=year)
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
