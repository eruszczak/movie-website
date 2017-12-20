from re import findall
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from accounts.models import UserFollow
from api.mixins import IsAuthenticatedMixin, GetTitleMixin, ToggleAPiView, GetUserMixin
from lists.models import Favourite
from titles.forms import TitleSearchForm
from titles.functions import create_or_update_rating, toggle_title_in_favourites, toggle_title_in_watchlist, \
    recommend_title
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


class TitleAddRatingView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        new_rating = request.POST.get('rating')
        # insert_as_new = request.POST.get('insert_as_new', False)
        insert_as_new = False
        try:
            title = Title.objects.get(pk=kwargs['pk'])
        except Title.DoesNotExist:
            return Response({'message': 'Title does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            message = create_or_update_rating(title, request.user, new_rating, insert_as_new)
            return Response({'message': message}, status=status.HTTP_200_OK)


class TitleDeleteRatingView(APIView):
    pass


class TitleToggleFavourite(IsAuthenticatedMixin, GetTitleMixin, APIView):

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        message = toggle_title_in_favourites(request.user, self.title, self.add)
        return Response({'message': message}, status=status.HTTP_200_OK)


class TitleToggleWatchlist(IsAuthenticatedMixin, GetTitleMixin, APIView):

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        message = toggle_title_in_watchlist(request.user, self.title, self.add)
        return Response({'message': message}, status=status.HTTP_200_OK)


class ToggleCurrentlyWatchingTV(IsAuthenticatedMixin, APIView):

    def post(self, request, *args, **kwargs):
        pass
        # add = request.POST.get('rating') == '1'
        # remove = not add
        # try:
        #     title = Title.objects.get(pk=kwargs['pk'])
        # except Title.DoesNotExist:
        #     return Response({'message': 'Title does not exist'}, status=status.HTTP_404_NOT_FOUND)
        # else:
        #     toggle_title_in_watchlist(request.user, title, add, remove)
        #     message = 'Added to watchlist' if add else 'Removed from watchlist'
        #     return Response({'message': message}, status=status.HTTP_200_OK)


class FollowUser(IsAuthenticatedMixin, GetUserMixin, APIView):

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        if self.add:
            UserFollow.objects.create(follower=self.request.user, followed=self.user)
            message = f'Followed {self.user.username}'
        else:
            UserFollow.objects.filter(follower=self.request.user, followed=self.user).delete()
            message = f'Unfollowed {self.user.username}'
        return Response({'message': message}, status=status.HTTP_200_OK)


class ReorderFavourite(IsAuthenticatedMixin, APIView):

    def post(self, request, *args, **kwargs):
        # try:
        #     user = User.objects.get(pk=kwargs['pk'])
        # except User.DoesNotExist:
        #     return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        # else:
        #     user_favourites = Favourite.objects.filter(user=user)
        #     new_title_order = request.POST.get('item_order')
        #     if new_title_order:
        #         new_title_order = findall('\d+', new_title_order)
        #         for new_position, title_pk in enumerate(new_title_order, 1):
        #             user_favourites.filter(title__pk=title_pk).update(order=new_position)
        #         return Response({'message': 'Changed order'}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecommendTitle(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user_ids = request.POST.getlist('recommended_user_ids[]')
        try:
            title = Title.objects.get(pk=kwargs['pk'])
        except Title.DoesNotExist:
            return Response({'message': 'Title does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            message = ''
            if user_ids:
                message = recommend_title(title, request.user, user_ids)
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
