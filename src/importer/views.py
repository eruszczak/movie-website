from os.path import join

from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.views.generic import FormView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.mixins import GetUserMixin
from importer.forms import ImportRatingsForm
from importer.tasks import task_import, task_export
from shared.mixins import LoginRequiredMixin
from titles.helpers import instance_required


WAIT_MESSAGE = 'You will be notified, when it is done.'


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
        default_storage.save(file_path, ContentFile(file.read()))
        task_import.delay(self.request.user.pk, file_path)
        messages.success(self.request, 'Refresh the page in a moment and your ratings should be imported')
        # with default_storage.open(file_path, 'wb+') as destination:
        #     for chunk in file.chunks():
        #         destination.write(chunk)
        # import_ratings_from_csv(self.request.user, file_path)
        return super().form_valid(form)


class ExportRatingsAPIView(LoginRequiredMixin, GetUserMixin, APIView):

    @instance_required
    def post(self, request, *args, **kwargs):
        task_export.delay(self.user.pk)
        # export_ratings(self.user)
        return Response({'message': 'Wait a moment, refresh the page and expand the management windows again and you should see link to your export', 'title': 'Export'}, status=status.HTTP_200_OK)


# class SyncRatingsAPIView(LoginRequiredMixin, APIView):
#
#     def post(self, request, *args, **kwargs):
#
#         return Response({'message': WAIT_MESSAGE, 'title': 'Sync ratings'}, status=status.HTTP_200_OK)
#
#
# class SyncWatchlistAPIView(LoginRequiredMixin, APIView):
#
#     def post(self, request, *args, **kwargs):
#         # def update_user_watchlist(user):
#         #     """
#         #     updates user's watchlist rss.imdb.com/user/<userid>/watchlist
#         #     """
#         #     itemlist = get_rss(user.imdb_id, 'watchlist')
#         #     if itemlist:
#         #         updated_titles = []
#         #         current_watchlist = []
#         #         count = 0
#         #         user_watchlist = Watchlist.objects.filter(user=user)
#         #         print('update_user_watchlist', user)
#         #         for obj in itemlist:
#         #             const, date = unpack_from_rss_item(obj, for_watchlist=True)
#         #             title = get_title_or_create(const)
#         #             if title:
#         #                 current_watchlist.append(const)
#         #                 obj, created = Watchlist.objects.get_or_create(user=user, title=title,
#         #                                                                defaults={'imdb': True, 'added_date': date})
#         #                 if created:
#         #                     count += 1
#         #                     if len(updated_titles) < 10:
#         #                         updated_titles.append(title)
#         #         no_longer_in_watchlist = user_watchlist.filter(imdb=True).exclude(title__const__in=current_watchlist)
#         #         deleted_titles = [w.title for w in no_longer_in_watchlist]
#         #         no_longer_in_watchlist.delete()
#         #         return {
#         #             'updated': (updated_titles, count),
#         #             'deleted': (deleted_titles, len(deleted_titles))
#         #         }
#         #     return None
#
#         return Response({'message': WAIT_MESSAGE, 'title': 'Sync ratings'}, status=status.HTTP_200_OK)
