from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from accounts.models import UserFollow
from api.mixins import IsAuthenticatedMixin, GetTitleMixin, ToggleAPIView, GetUserMixin
from lists.models import Favourite
from titles.forms import TitleSearchForm
from titles.functions import create_or_update_rating, toggle_title_in_favourites, toggle_title_in_watchlist, \
    recommend_title, follow_user
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
    lookup_field = 'slug'


class AddRatingAPIView(IsAuthenticatedMixin, GetTitleMixin, APIView):

    def post(self, request, *args, **kwargs):
        message = self.set_instance(**kwargs)
        if message:
            return message

        new_rating = request.POST.get('rating')
        insert_as_new = False  # request.POST.get('insert_as_new', False)
        message = create_or_update_rating(self.title, request.user, new_rating, insert_as_new)
        return Response({'message': message}, status=status.HTTP_200_OK)


class TitleDeleteRatingView(APIView):
    pass


class ToggleFavouriteAPIView(IsAuthenticatedMixin, ToggleAPIView, GetTitleMixin, APIView):

    def post(self, request, *args, **kwargs):
        message = self.set_instance(**kwargs)
        if message:
            return message

        message = toggle_title_in_favourites(request.user, self.title, self.toggle_active)
        return Response({'message': message}, status=status.HTTP_200_OK)


class ToggleWatchlistAPIView(IsAuthenticatedMixin, ToggleAPIView, GetTitleMixin, APIView):

    def post(self, request, *args, **kwargs):
        message = self.set_instance(**kwargs)
        if message:
            return message

        message = toggle_title_in_watchlist(request.user, self.title, self.toggle_active)
        return Response({'message': message}, status=status.HTTP_200_OK)


class ToggleCurrentlyWatchingTV(IsAuthenticatedMixin, ToggleAPIView, GetUserMixin, GetTitleMixin, APIView):
    title_url_kwarg = 'pk_title'
    user_url_kwarg = 'pk_user'

    def post(self, request, *args, **kwargs):
        print(self.__class__.mro())
        return super().post(request, *args, **kwargs)
        # todo: problem because I cant call super in GetUserMixin, and GetTitleMixin won't be called


class ToggleFollowUser(IsAuthenticatedMixin, ToggleAPIView, GetUserMixin, APIView):

    def post(self, request, *args, **kwargs):
        message = self.set_instance(**kwargs)
        if message:
            return message

        message = follow_user(self.request.user, self.user, self.toggle_active)
        return Response({'message': message}, status=status.HTTP_200_OK)


class ReorderFavourite(IsAuthenticatedMixin, GetUserMixin, APIView):

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        # user_favourites = Favourite.objects.filter(user=user)
        # new_title_order = request.POST.get('item_order')
        # if new_title_order:
        #     new_title_order = findall('\d+', new_title_order)
        #     for new_position, title_pk in enumerate(new_title_order, 1):
        #         user_favourites.filter(title__pk=title_pk).update(order=new_position)
        #     return Response({'message': 'Changed order'}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecommendTitleAPIView(IsAuthenticatedMixin, GetTitleMixin, APIView):

    def post(self, request, *args, **kwargs):
        message = self.set_instance(**kwargs)
        if message:
            return message

        user_ids = request.POST.getlist('recommended_user_ids[]')
        message = ''
        if user_ids:
            message = recommend_title(self.title, request.user, user_ids)
        return Response({'message': message}, status=status.HTTP_200_OK)


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

        serializer_title = TitleSerializer(queryset_title[:len_titles], many=True)  # context={'request': request}
        serializer_person = PersonSerializer(queryset_person[:len_persons], many=True)

        return Response({
            'titles': serializer_title.data,
            'persons': serializer_person.data,
            'action': {
                'url': f'{reverse("title-list")}?{urlencode(request.GET)}'
            }
        }, status=status.HTTP_200_OK)
