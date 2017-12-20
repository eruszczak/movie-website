from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from titles.models import Title


User = get_user_model()


class IsAuthenticatedMixin:
    permission_classes = (IsAuthenticated,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GetObjectMixin:
    model = None
    instance = None
    url_kwarg = 'pk'

    def __init__(self, *args, **kwargs):
        """
        Url kwarg name will almost always be pk, but if I will be using eg. two derived classes together,
        url kwargs must have a different name. This will allow me for this:
        MyClass(GetTitleMixin, GetUserMixin):
            title_url_kwarg = 'title_pk'
            user_url_kwarg = 'user_pk'
        """
        super().__init__(*args, **kwargs)
        print(self.kwargs)
        # kwargs = {'pk': 42, 'title_pk': 10, 'user_pk': 100}

        self.model_name = self.model.__name__
        self.model_instance_name = self.model_name.lower()
        model_url_kwarg = f'{self.model_instance_name}_url_kwarg'
        self.url_kwarg = getattr(self, model_url_kwarg, self.url_kwarg)

        try:
            lookup = {self.url_kwarg: kwargs[self.url_kwarg]}
            print(lookup)
            self.instance = self.model.objects.get(**lookup)
        except self.model.DoesNotExist:
            pass

        # eg. if model = Title, this will set self.title
        setattr(self, self.model_instance_name, self.instance)

    def post(self, request, *args, **kwargs):
        print('get_object post')
        if not self.instance:
            return Response({'message': f'{self.model_name} does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return super().post(request, *args, **kwargs)


class ToggleAPiView:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add = kwargs['request'].POST.get('rating') == '1'


class GetTitleMixin(GetObjectMixin):
    model = Title


class GetUserMixin(GetObjectMixin):
    model = User
