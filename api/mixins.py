from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from titles.models import Title


User = get_user_model()


class IsAuthenticatedMixin:
    permission_classes = (IsAuthenticated,)


class ToggleAPIView:
    toggle_active = None

    def init_data(self):
        self.toggle_active = self.request.POST.get('rating') == '1'


class GetObjectMixin:
    model = None
    url_kwarg = 'pk'
    kwarg_field = 'pk'

    def set_instance(self, **kwargs):
        self.init_data()
        try:
            lookup = {self.kwarg_field: kwargs[self.url_kwarg]}
            setattr(self, self.model.__name__.lower(), self.model.objects.get(**lookup))
            return None
        except self.model.DoesNotExist:
            return Response({'message': f'{self.model.__name__} does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def init_data(self):
        pass


class GetTitleMixin(GetObjectMixin):
    model = Title
    title = None


class GetUserMixin(GetObjectMixin):
    model = User
    user = None
