import io
import csv
from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.db.models import Count, Case, When, IntegerField, OuterRef, Subquery, F, Avg
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DetailView

from titles.models import Title, Rating
from accounts.models import UserFollow
from accounts.forms import UserUpdateForm
from accounts.functions import validate_imported_ratings, create_csv_with_user_ratings
from common.prepareDB_utils import convert_to_datetime

User = get_user_model()


# def export_ratings(request, username):
#     """
#     exports to a csv file all of user's ratings, so they can be imported later (using view defined below)
#     file consists of lines in format: tt1234567,2017-05-23,7
#     """
#     response = HttpResponse(content_type='text/csv')
#     headers = ['const', 'rate_date', 'rate']
#     user_ratings = Rating.objects.filter(user__username=username).select_related('title')
#
#     writer = csv.DictWriter(response, fieldnames=headers, lineterminator='\n')
#     writer.writeheader()
#     count_ratings, count_titles = create_csv_with_user_ratings(writer, user_ratings)
#
#     filename = '{}_ratings_for_{}_titles_{}'.format(count_ratings, count_titles, datetime.now().strftime('%Y-%m-%d'))
#     response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
#     return response
#
#
# @login_required
# @require_POST
# def import_ratings(request):
#     """
#     from exported csv file import missing ratings. it doesn't add new titles, only new ratings
#     file consists of lines in format: tt1234567,2017-05-23,7
#     """
#     user = User.objects.get(user=request.user)
#     uploaded_file = request.FILES['csv_ratings']
#     file = uploaded_file.read().decode('utf-8')
#     io_string = io.StringIO(file)
#     is_valid, message = validate_imported_ratings(uploaded_file, io_string)
#     if not is_valid:
#         messages.info(request, message)
#         return redirect(user)
#
#     # TODO make a class that handles serialization and deserialization
#     reader = csv.DictReader(io_string)
#     total_rows = 0
#     created_count = 0
#     for row in reader:
#         total_rows += 1
#         const, rate_date, rate = row['const'], row['rate_date'], row['rate']
#         title = Title.objects.filter(const=const).first()
#         rate_date = convert_to_datetime(row['rate_date'], 'exported_from_db')
#
#         if title and rate_date:
#             obj, created = Rating.objects.get_or_create(
#                 user=request.user, title=title, rate_date=rate_date, defaults={'rate': rate}
#             )
#             if created:
#                 created_count += 1
#     messages.info(request, 'imported {} out of {} ratings'.format(created_count, total_rows))
#     return redirect(user)


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated')
        return super().form_valid(form)


class UserListView(ListView):
    template_name = 'accounts/user_list.html'
    paginate_by = 20
    searched_title = None
    model = User

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get('const'):
            self.searched_title = get_object_or_404(Title, const=self.request.GET['const'])
            queryset = queryset.filter(rating__title=self.searched_title).annotate(
                user_rate=Subquery(
                    Rating.objects.filter(
                        user=OuterRef('pk'), title=OuterRef('rating__title')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            ).distinct()
        else:
            queryset = User.objects.annotate(num=Count('rating')).order_by('-num', '-username')

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                already_follows=Subquery(
                    UserFollow.objects.filter(follower=self.request.user, followed=OuterRef('pk')).values('pk')
                )
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.searched_title:
            context.update({
                'title': self.searched_title,
            })
        return context


class UserDetailView(DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    titles_in_a_row = 6
    is_owner = False
    common = None
    is_other_user = False
    user = None
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.is_owner = self.object == self.request.user
        self.is_other_user = self.request.user.is_authenticated and not self.is_owner
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        return self.model.objects.filter(username=self.kwargs['username']).annotate(
            total_ratings=Count('rating'),
            total_movies=Count(Case(When(rating__title__type__name='movie', then=1), output_field=IntegerField())),  # distinct
            total_series=Count(Case(When(rating__title__type__name='series', then=1), output_field=IntegerField())),  # distinct
            # total_followers=Count(Case(When(userfollow__followed__pk=F('pk'), then=1), output_field=IntegerField())),
        ).get()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.is_other_user:
            ratings = Rating.objects.filter(user=self.object).select_related('title')
        else:
            ratings = Rating.objects.filter(user=self.object).annotate(
                user_rate=Subquery(
                    Rating.objects.filter(
                        user=self.request.user, title=OuterRef('title')
                    ).order_by('-rate_date').values('rate')[:1])
            ).select_related('title')
            context.update({
                'already_follows': UserFollow.objects.filter(follower=self.request.user, followed=self.object).exists(),
                'comparision': self.get_ratings_comparision()
            })

        followed = UserFollow.objects.filter(follower=self.object).values_list('followed', flat=True)
        context.update({
            'is_other_user': self.is_other_user,
            'is_owner': self.is_owner,
            'rating_list': ratings[:self.titles_in_a_row],
            'total_followers': UserFollow.objects.filter(followed=self.object).count(),
            'total_followed': len(followed),
            'feed': Rating.objects.filter(user__in=followed).select_related('title', 'user').order_by('-rate_date')[:10]
        })
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        # if self.request.POST.get('confirm-nick'):
        #     if self.request.POST['confirm-nick'] == self.request.user.username:
        #         deleted_count = Rating.objects.filter(user=self.request.user).delete()[0]
        #         message = 'You have deleted your {} ratings'.format(deleted_count)
        #     else:
        #         message = 'Confirmation failed. Wrong username. No ratings deleted.'
        #     messages.info(self.request, message, extra_tags='safe')
        # elif self.is_owner:
        #     message = ''
        #     if self.request.POST.get('update_csv'):
        #         message = update_ratings_using_csv(self.object)
        #     elif self.request.POST.get('update_rss') and self.object.imdb_id:
        #         message = update_ratings(self.object)
        #     elif self.request.POST.get('update_watchlist') and self.object.imdb_id:
        #         message = update_watchlist(self.object)
        #     messages.info(self.request, message, extra_tags='safe')
        return redirect(self.object)

    def get_ratings_comparision(self):
        """
        gets additional context for a user who visits somebody else's profile
        """
        common_titles = Title.objects.filter(
            rating__user=self.object).filter(rating__user=self.request.user).distinct().annotate(
            user_rate=Subquery(
                Rating.objects.filter(
                    user=self.object, title=OuterRef('pk')
                ).order_by('-rate_date').values('rate')[:1]
            ),
            request_user_rate=Subquery(
                Rating.objects.filter(
                    user=self.request.user, title=OuterRef('pk')
                ).order_by('-rate_date').values('rate')[:1]
            )
        )
        common_titles_length = common_titles.count()
        if common_titles_length:
            titles_user_rate_higher = common_titles.filter(user_rate__gt=F('request_user_rate'))
            titles_user_rate_lower = common_titles.filter(user_rate__lt=F('request_user_rate'))
            titles_rated_the_same = common_titles.filter(user_rate=F('request_user_rate'))
            titles_user_liked = Title.objects.filter(rating__user=self.object, rating__rate__gte=7).exclude(
                rating__user=self.request.user).distinct().annotate(
                user_rate=Subquery(
                    Rating.objects.filter(
                        user=self.object, title=OuterRef('pk')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            )

            averages = common_titles.aggregate(user=Avg('user_rate'), request_user=Avg('request_user_rate'))

            return {
                'common_titles_length': common_titles_length,
                'titles_user_rate_higher': titles_user_rate_higher,
                'titles_user_rate_lower': titles_user_rate_lower,
                'titles_rated_the_same': titles_rated_the_same,
                'averages': averages,
                'percentage': round((common_titles_length / self.object.count_titles) * 100, 2),
                'titles_user_liked': titles_user_liked
            }


