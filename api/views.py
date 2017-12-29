from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from django.db.transaction import atomic
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from api.mixins import IsAuthenticatedMixin, GetTitleMixin, GetUserMixin
from lists.models import Favourite
from titles.forms import TitleSearchForm, RateForm
from titles.utils import (
    toggle_favourite, toggle_watchlist, toggle_currentlywatchingtv, toggle_userfollow
)
from titles.helpers import instance_required
from titles.models import Rating, Title, Person
from .serializers import RatingListSerializer, TitleSerializer, PersonSerializer

User = get_user_model()


class SetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'per_page'


class RatingsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingListSerializer
    pagination_class = SetPagination

    def get_queryset(self):
        if self.request.GET.get('u'):
            self.queryset = Rating.objects.filter(user__username=self.request.GET['u'])
        return self.queryset


class TitleDetailView(RetrieveAPIView):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CreateUpdateRatingAPIView(IsAuthenticatedMixin, GetTitleMixin, APIView):

    @instance_required
    def post(self, request, *args, **kwargs):
        """create new rating (with today's date) or update latest rating's rate"""
        data = {'rate': request.POST['rating']}
        try:
            instance = Rating.objects.filter(user=self.request.user, title=self.title).latest('rate_date')
        except Rating.DoesNotExist:
            data['rate_date'] = now().date()
            form = RateForm(user=self.request.user, title=self.title, data=data)
            message = 'Created rating'
        else:
            # instance already has rate_date but this field is required (also, do not need to pass title, user here)
            data['rate_date'] = instance.rate_date
            form = RateForm(data=data, instance=instance)
            message = 'Updated rating'

        if form.is_valid():
            form.save()
            return Response({'message': message}, status=status.HTTP_200_OK)

        message = 'Error'
        # message = form.errors
        return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)


class DeleteRatingAPIView(IsAuthenticatedMixin, GetTitleMixin, APIView):

    @instance_required
    def post(self, request, *args, **kwargs):
        try:
            current_rating = Rating.objects.filter(user=request.user, title=self.title).latest('rate_date')
        except Rating.DoesNotExist:
            return Response({'message': 'Rating doesn\'t exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            rate_date = current_rating.rate_date
            current_rating.delete()
            return Response({'message': f'Removed rating from {rate_date}'}, status=status.HTTP_200_OK)


class ClearRatingsAPIView(IsAuthenticatedMixin, APIView):

    def post(self, request, *args, **kwargs):
        Rating.objects.filter(user=self.request.user).delete()
        return Response({'message': f'Ratings have been cleared'}, status=status.HTTP_200_OK)


class ToggleFavouriteAPIView(IsAuthenticatedMixin, GetTitleMixin, APIView):

    @instance_required
    def post(self, request, *args, **kwargs):
        try:
            created, message = toggle_favourite(request.user, self.title)
        except ValidationError as e:
            return Response({'message': '. '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': message, 'created': created}, status=status.HTTP_200_OK)


class ToggleWatchlistAPIView(IsAuthenticatedMixin, GetTitleMixin, APIView):

    @instance_required
    def post(self, request, *args, **kwargs):
        try:
            created, message = toggle_watchlist(request.user, self.title)
        except ValidationError as e:
            return Response({'message': '. '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': message, 'created': created}, status=status.HTTP_200_OK)


class ToggleCurrentlyWatchingTV(IsAuthenticatedMixin, GetTitleMixin, APIView):

    @instance_required
    def post(self, request, *args, **kwargs):
        created, message = toggle_currentlywatchingtv(self.title, self.request.user)
        return Response({'message': message, 'created': created}, status=status.HTTP_200_OK)


class ToggleFollowUser(IsAuthenticatedMixin, GetUserMixin, APIView):

    @instance_required
    def post(self, request, *args, **kwargs):
        created, message = toggle_userfollow(self.request.user, self.user)
        return Response({'message': message, 'created': created}, status=status.HTTP_200_OK)


class ReorderFavourite(IsAuthenticatedMixin, APIView):

    def post(self, request, *args, **kwargs):
        favourite_list = Favourite.objects.filter(user=request.user)
        new_index, old_index, change = self.get_indexes()
        if new_index and old_index and change != 0 and self.valid_indexes(new_index, old_index, favourite_list):
            with atomic():
                # get item that was moved and exclude its order before updating
                # Its order will be changed manually
                moved_item = favourite_list.get(order=old_index)

                # if item has moved from #3 to #5 (or reversed),
                # this will either decrease (or increase) order of #4 (middle items)
                favourite_list = favourite_list.exclude(order=moved_item.order)
                if change > 0:
                    favourite_list.filter(Q(order__gte=new_index) & Q(order__lt=old_index)).update(order=F('order') + 1)
                else:
                    favourite_list.filter(Q(order__lte=new_index) & Q(order__gt=old_index)).update(order=F('order') - 1)

                # moved_item hasn't been updated yet, so right now 2 items have order==old_index
                moved_item.order = new_index
                moved_item.save()

            return Response({'message': 'Changed order.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Nothing has changed.'}, status=status.HTTP_200_OK)

    def get_indexes(self):
        try:
            new_index = int(self.request.POST.get('newIndex')) + 1
            old_index = int(self.request.POST.get('oldIndex')) + 1
            return new_index, old_index, old_index - new_index
        except (ValueError, TypeError):
            return None, None, 0

    @staticmethod
    def valid_indexes(index1, index2, fav_qs):
        """returns true if both indexes are not bigger than last favourite title's order"""
        max_index = max(fav_qs.values_list('order', flat=True))
        return index1 <= max_index and index2 <= max_index


class SearchAPIView(APIView):
    MAX_RESULTS = 15

    def get(self, request, *args, **kwargs):
        queryset_title = Title.objects.all()
        queryset_title = TitleSearchForm(request.GET).search(queryset_title)
        queryset_person = Person.objects.filter(name__icontains=request.GET['keyword'])

        len_titles, len_qs_title = 10, queryset_title.count()
        len_persons, len_qs_person = 5, queryset_person.count()
        if len_qs_title < len_titles:
            len_persons = self.MAX_RESULTS - len_qs_title

        if len_qs_person < len_persons:
            len_titles = self.MAX_RESULTS - len_qs_person

        serializer_title = TitleSerializer(queryset_title[:len_titles], many=True)
        serializer_person = PersonSerializer(queryset_person[:len_persons], many=True)

        return Response({
            'titles': serializer_title.data,
            'persons': serializer_person.data,
            'action': {
                'url': f'{reverse("title-list")}?{urlencode(request.GET)}'
            }
        }, status=status.HTTP_200_OK)
