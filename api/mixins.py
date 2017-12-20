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


# class GetObjectMixin:
#     model = None
#     instance = None
#
#     def post(self, request, *args, **kwargs):
#         print(kwargs)
#         """
#         Url kwarg name will almost always be pk, but if I will be using eg. two derived classes together,
#         url kwargs must have a different name. Example:
#         MyClass(GetTitleMixin, GetUserMixin):
#             title_url_kwarg = 'pk_title'
#             user_url_kwarg = 'username_user'
#         This means that GetTitleMixin's url_kwarg is pk. But for other mixin it's username
#         """
#         # kwargs = {'pk': 42, 'title_pk': 10, 'user_pk': 100}
#
#         self.model_name = self.model.__name__
#         self.model_instance_name = self.model_name.lower()
#         model_url_kwarg = f'{self.model_instance_name}_url_kwarg'
#         url_kwarg = getattr(self, model_url_kwarg, None)
#         if url_kwarg:
#             field_name = url_kwarg.split('_')[0]
#         else:
#             url_kwarg = 'pk'
#             field_name = 'pk'
#         try:
#             lookup = {field_name: kwargs[url_kwarg]}
#             print(lookup)
#             self.instance = self.model.objects.get(**lookup)
#         except self.model.DoesNotExist:
#             pass
#
#         # eg. if model = Title, this will set self.title
#         setattr(self, self.model_instance_name, self.instance)
#
#         print('get_object post')
#         if not self.instance:
#             return Response({'message': f'{self.model_name} does not exist'}, status=status.HTTP_404_NOT_FOUND)
#
#         try:
#             return super().post(request, *args, **kwargs)
#         except AttributeError:
#             return Response({})

class GetObjectMixin:
    model = None

    def set_instance(self, **kwargs):
        self.init_data()
        try:
            setattr(self, self.model.__name__.lower(), self.model.objects.get(pk=kwargs['pk']))
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

