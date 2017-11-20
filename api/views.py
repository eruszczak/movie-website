from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
from re import findall

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination

from titles.models import Rating, Title, Favourite
from accounts.models import UserFollow
from .serializers import RatingListSerializer, TitleSerializer
from common.sql_queries import rating_distribution
from titles.functions import create_or_update_rating, toggle_title_in_favourites, toggle_title_in_watchlist

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


class TitleToggleFavourite(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        add = request.POST.get('rating') == '1'
        remove = not add
        try:
            title = Title.objects.get(pk=kwargs['pk'])
        except Title.DoesNotExist:
            return Response({'message': 'Title does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            toggle_title_in_favourites(request.user, title, add, remove)
            message = 'Added to favourites' if add else 'Removed from favourites'
            return Response({'message': message}, status=status.HTTP_200_OK)


class TitleToggleWatchlist(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        add = request.POST.get('rating') == '1'
        remove = not add
        try:
            title = Title.objects.get(pk=kwargs['pk'])
        except Title.DoesNotExist:
            return Response({'message': 'Title does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            toggle_title_in_watchlist(request.user, title, add, remove)
            message = 'Added to watchlist' if add else 'Removed from watchlist'
            return Response({'message': message}, status=status.HTTP_200_OK)


class FollowUser(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        add = request.POST.get('rating') == '1'
        remove = not add
        try:
            user = User.objects.get(pk=kwargs['pk'])
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if add:
                UserFollow.objects.create(follower=self.request.user, followed=user)
            elif remove:
                UserFollow.objects.filter(follower=self.request.user, followed=user).delete()
            message = 'You {} {}'.format('followed' if add else 'unfollowed', user.username)
            return Response({'message': message}, status=status.HTTP_200_OK)


class ReorderFavourite(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(pk=kwargs['pk'])
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user_favourites = Favourite.objects.filter(user=user)
            new_title_order = request.POST.get('item_order')
            if new_title_order:
                new_title_order = findall('\d+', new_title_order)
                for new_position, title_pk in enumerate(new_title_order, 1):
                    user_favourites.filter(title__pk=title_pk).update(order=new_position)
                return Response({'message': 'Changed order'}, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_204_NO_CONTENT)


class Search(APIView):

    def get(self, request, *args, **kwargs):
        # t = Title.objects.filter(name__icontains=kwargs.get('name', 'dare'))
        t = Title.objects.all()[:20]
        serializer = TitleSerializer(t, many=True)
        # serializer = TitleSerializer(t, many=True, context={'request': request})
        return Response({'results': serializer.data}, status=status.HTTP_200_OK)
