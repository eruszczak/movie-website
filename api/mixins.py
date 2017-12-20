from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from titles.models import Title


User = get_user_model()


class IsAuthenticatedMixin:
    permission_classes = (IsAuthenticated,)


class ToggleAPiView:
    add = False

    def post(self, request, *args, **kwargs):
        self.add = request.POST.get('rating') == '1'


class GetTitleMixin(ToggleAPiView):
    title = None

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        try:
            self.title = Title.objects.get(pk=kwargs['pk'])
        except Title.DoesNotExist:
            return Response({'message': 'Title does not exist'}, status=status.HTTP_404_NOT_FOUND)


class GetUserMixin(ToggleAPiView):
    user = None

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        try:
            self.user = User.objects.get(pk=kwargs['pk'])
        except Title.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
