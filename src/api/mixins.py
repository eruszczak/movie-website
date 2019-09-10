from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from titles.models import Title


User = get_user_model()


class IsAuthenticatedMixin:
    permission_classes = (IsAuthenticated,)


class GetObjectMixin:
    """
    Class that is meant to be used with instance_required decorator, which is used around APIView's post handler.
    APIView must inherit any subclass of this class (eg. GetTitleMixin).
    Decorator makes sure to call set_instance method from this class.
    Example:
        class ExportRatingsAPIView(GetUserMixin, APIView):
            @instance_required
            def post(self, request, *args, **kwargs):
                self.user == User.objects.get(pk=kwargs['pk'])
        url(r'^(?P<pk>\d+)/export', views.ExportRatingsAPIView.as_view()),
    In post method there will be accessible self.user or it will return `User does not exist`
    """
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
