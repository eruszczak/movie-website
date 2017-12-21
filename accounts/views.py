from django.contrib.auth import get_user_model
from django.db.models import Count, OuterRef, Subquery, F, Avg, Exists
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, UpdateView, DetailView

from titles.constants import SERIES, MOVIE
from titles.helpers import SubqueryCount
from titles.models import Title, Rating
from accounts.models import UserFollow
from accounts.forms import UserUpdateForm


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
        return super().get_queryset().get(pk=self.request.user.pk)

    def get_success_url(self):
        messages.success(self.request, 'Settings updated.')
        return self.get_object().edit_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['original_instance'] = self.request.user
        return kwargs


class UserListView(ListView):
    template_name = 'accounts/user_list.html'
    paginate_by = 20
    searched_title = None
    model = User

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get('imdb_id'):
            self.searched_title = get_object_or_404(Title, imdb_id=self.request.GET['imdb_id'])
            queryset = queryset.filter(rating__title=self.searched_title).annotate(
                user_rate=Subquery(
                    Rating.objects.filter(
                        user=OuterRef('pk'), title=OuterRef('rating__title')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            ).distinct()

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                already_follows=Exists(UserFollow.objects.filter(follower=self.request.user, followed=OuterRef('pk')))
            )
        return queryset.annotate(
            # followers_count=Subquery(
            #     UserFollow.objects.filter(follower=OuterRef('pk')).count()
            # ),
            titles_count=Count('rating')
        ).order_by('-titles_count')

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
    limit = 15

    def get_queryset(self):
        queryset = super().get_queryset().filter(username=self.kwargs['username']).annotate(
            total_movies=SubqueryCount(
                Rating.objects.filter(title__type=MOVIE, user=OuterRef('pk')).order_by().distinct('title')
            ),
            total_series=SubqueryCount(
                Rating.objects.filter(title__type=SERIES, user=OuterRef('pk')).order_by().distinct('title')
            ),
            total_followers=SubqueryCount(
                UserFollow.objects.filter(followed=OuterRef('pk'))
            ),
            total_ratings=Count('rating'),
        )

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                already_follows=Exists(UserFollow.objects.filter(follower=self.request.user, followed=OuterRef('pk')))
            )
        return queryset

    def get_object(self, queryset=None):
        return self.get_queryset().get()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_owner = self.object.pk == self.request.user.pk
        is_other_user = self.request.user.is_authenticated and not is_owner

        ratings = Rating.objects.filter(user=self.object).select_related('title')
        currently_watching = Title.objects.filter(currentlywatchingtv__user=self.object).annotate(
            user_rate=Subquery(
                Rating.objects.filter(user=self.object, title=OuterRef('pk')).order_by('-rate_date').values('rate')[:1]
            )
        )

        if self.request.user.is_authenticated:
            ratings = ratings.annotate(
                request_user_rate=Subquery(
                    Rating.objects.filter(
                        user=self.request.user, title=OuterRef('title')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            )
            currently_watching = currently_watching.annotate(
                request_user_rate=Subquery(
                    Rating.objects.filter(
                        user=self.request.user, title=OuterRef('pk')
                    ).order_by('-rate_date').values('rate')[:1]
                )
            )

        if is_other_user:
            context.update({
                'already_follows': UserFollow.objects.filter(follower=self.request.user, followed=self.object).exists(),
                'comparision': self.get_ratings_comparision()
            })

        context.update({
            'is_other_user': is_other_user,
            'is_owner': is_owner,
            'rating_list': ratings[:self.limit],
            'currently_watching': currently_watching[:self.limit],
            'feed': Rating.objects.filter(
                user__in=UserFollow.objects.filter(follower=self.object).values_list('followed', flat=True)
            ).select_related('title', 'user').order_by('-rate_date')[:self.limit]
        })
        return context

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

            distinct_titles_count = self.object.total_movies + self.object.total_series
            return {
                'common_titles_length': common_titles_length,
                'averages': common_titles.aggregate(user=Avg('user_rate'), request_user=Avg('request_user_rate')),
                'percentage': round((common_titles_length / distinct_titles_count) * 100, 2),

                'titles_user_rate_higher': titles_user_rate_higher[:self.limit],
                'titles_user_rate_lower': titles_user_rate_lower[:self.limit],
                'titles_rated_the_same': titles_rated_the_same[:self.limit],
                'titles_user_liked': titles_user_liked[:self.limit]
            }


