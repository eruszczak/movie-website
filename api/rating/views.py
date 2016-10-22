import calendar
from datetime import datetime
from collections import OrderedDict
from utils.utils import build_url
from chart.charts import count_for_month_lists

from movie.models import Rating
from django.db.models import Q, Count

from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from .pagination import SetPagination
from .serializers import *


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