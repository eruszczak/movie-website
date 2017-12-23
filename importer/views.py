from os.path import join

from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views.generic import FormView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.mixins import GetUserMixin
from importer.forms import ImportRatingsForm
from importer.utils import import_ratings_from_csv, export_ratings
from shared.mixins import LoginRequiredMixin
from titles.helpers import instance_required


class ImportRatingsFormView(LoginRequiredMixin, FormView):
    form_class = ImportRatingsForm

    def get_success_url(self):
        return self.request.user.get_absolute_url()

    def form_invalid(self, form):
        message = 'There was an error with import'
        if form['csv_file'].errors:
            message = f"Error with uploaded file for import: {form['csv_file'].errors.as_text().lstrip('* ')}"

        messages.error(self.request, message)
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        user_tmp_folder = self.request.user.get_temp_folder_path(absolute=True, create=True)
        file = form.cleaned_data['csv_file']
        file_path = join(user_tmp_folder, file.name)
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
        path = default_storage.save(file_path, ContentFile(file.read()))
        print('importing', path)
        import_ratings_from_csv(self.request.user, path)
        messages.success(self.request, 'You will be notified, when import is done.')
        return super().form_valid(form)


class ExportRatingsAPIView(GetUserMixin, APIView):

    @instance_required
    def post(self, request, *args, **kwargs):
        message = 'export'
        # todo: these files can be cached for a few days
        # todo: test if error is displayed if no user

        message = export_ratings(self.user)
        return Response({'message': message, 'title': 'Export'}, status=status.HTTP_200_OK)
        # todo: this must create file in celery. then user be notified when he can download the file