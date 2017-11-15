import io
import csv
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, Case, When, BooleanField, IntegerField, OuterRef, Subquery
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DetailView

from titles.models import Title, Rating
from accounts.models import UserFollow
from accounts.forms import EditProfileForm
from accounts.functions import (
    update_ratings_using_csv,
    update_ratings,
    update_watchlist,
    validate_imported_ratings,
    create_csv_with_user_ratings
)
from common.sql_queries import avgs_of_2_users_common_curr_ratings, titles_rated_higher_or_lower
from common.prepareDB_utils import convert_to_datetime

User = get_user_model()


def export_ratings(request, username):
    """
    exports to a csv file all of user's ratings, so they can be imported later (using view defined below)
    file consists of lines in format: tt1234567,2017-05-23,7
    """
    response = HttpResponse(content_type='text/csv')
    headers = ['const', 'rate_date', 'rate']
    user_ratings = Rating.objects.filter(user__username=username).select_related('title')

    writer = csv.DictWriter(response, fieldnames=headers, lineterminator='\n')
    writer.writeheader()
    count_ratings, count_titles = create_csv_with_user_ratings(writer, user_ratings)

    filename = '{}_ratings_for_{}_titles_{}'.format(count_ratings, count_titles, datetime.now().strftime('%Y-%m-%d'))
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
    return response


@login_required
@require_POST
def import_ratings(request):
    """
    from exported csv file import missing ratings. it doesn't add new titles, only new ratings
    file consists of lines in format: tt1234567,2017-05-23,7
    """
    user = User.objects.get(user=request.user)
    uploaded_file = request.FILES['csv_ratings']
    file = uploaded_file.read().decode('utf-8')
    io_string = io.StringIO(file)
    is_valid, message = validate_imported_ratings(uploaded_file, io_string)
    if not is_valid:
        messages.info(request, message)
        return redirect(user)

    # TODO make a class that handles serialization and deserialization
    reader = csv.DictReader(io_string)
    total_rows = 0
    created_count = 0
    for row in reader:
        total_rows += 1
        const, rate_date, rate = row['const'], row['rate_date'], row['rate']
        title = Title.objects.filter(const=const).first()
        rate_date = convert_to_datetime(row['rate_date'], 'exported_from_db')

        if title and rate_date:
            obj, created = Rating.objects.get_or_create(user=request.user, title=title, rate_date=rate_date,
                                                        defaults={'rate': rate})
            if created:
                created_count += 1
    messages.info(request, 'imported {} out of {} ratings'.format(created_count, total_rows))
    return redirect(user)


class UserUpdateView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/user_edit.html'

    # only owner can edit
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
            # newest = Rating.objects.filter(user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')
            # queryset = queryset.filter(rating__title=self.searched_title).annotate(
            #     user_rate=Subquery(newest.values('rate')[:1]))
            # # newest = Rating.objects.filter(user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')
            # for x in queryset:
            #     print(x.user_rate)
            queryset = queryset.filter(rating__title=self.searched_title).extra(select={
                'user_rate': """SELECT rating.rate FROM titles_rating as rating, titles_title as title
                    WHERE rating.title_id = title.id AND rating.user_id = accounts_user.id AND title.id = %s
                    ORDER BY rating.rate_date DESC LIMIT 1"""
            }, select_params=[self.searched_title.pk])#.order_by('-current_rating', '-username')
            # if self.request.user.is_authenticated:
            #     pass

            #     qs = User.objects.filter(rating__title=self.searched_title).annotate(
            #         has_in_watchlist=Count(
            #             Case(
            #                 When(title__watchlist__user=self.request.user, title__watchlist__deleted=False, then=1),
            #                 output_field=IntegerField()
            #             )
            #         ),
            #         has_in_favourites=Count(
            #             Case(When(title__favourite__user=self.request.user, then=1), output_field=IntegerField())
            #         ),
            #     )
            # queryset = self.get_users_who_saw_a_title()
        else:
            queryset = User.objects.annotate(num=Count('rating')).order_by('-num', '-username')

        if self.request.user.is_authenticated:
            # q = queryset.annotate(
            #     already_follows=Count(
            #         Case(When(userfollow__follower=self.request.user, then=1), output_field=IntegerField())
            #     ),
            #     # test=Count('userfollow__follower')
            # )
            print('request user', self.request.user.pk)
            print(['{} follows {}'.format(x.follower.pk, x.followed.pk) for x in UserFollow.objects.all()])
            print()
            print(User.objects.filter(userfollow__follower=self.request.user))
            # request: test, returns test  todo: should return test2 because test follows test2
            # request: test2, return test2  todo: again wrong!

            print(User.objects.filter(userfollow__followed=self.request.user))
            # request: test, returns test2 because test2 is followed by test
            # request: test2, returns test because test is followed by test

            # print(User.objects.filter(userfollow__followed=User.objects.get(username='test2')))  #
            print()
            # for x in q:
            #     print(x, x.already_follows)
            queryset = queryset.extra(select={
                'already_follows': """SELECT 1 FROM accounts_userfollow as followage
                    WHERE followage.follower_id = %s and followage.followed_id = accounts_user.id""",
            }, select_params=[self.request.user.pk])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.searched_title:
            context.update({
                'title': self.searched_title,
                # 'query_string': '?s=' + self.request.GET['s'] + '&page=',
                # 'page_title': 'Users who saw {}'.format(str(self.searched_title))
            })
        return context


# todo this must be UpdateView
class UserDetailView(DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    url_lookup_kwarg = 'username'
    titles_in_a_row = 6
    is_owner = False  # checks if a request user is an owner of the profile
    common = None
    is_other_user = False  # authenticated user who is not an owner of the profile
    user = None
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.is_owner = self.object == self.request.user
        self.is_other_user = self.request.user.is_authenticated and not self.is_owner
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        return self.model.objects.get(username=self.kwargs[self.url_lookup_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.is_other_user:
            context.update({
                'already_follows': UserFollow.objects.filter(follower=self.request.user, followed=self.object).exists()
            })
            # self.common = self.get_user_ratings()
            # newest = Rating.objects.filter(user=self.request.user, title=OuterRef('pk')).order_by('-rate_date')
            # ratings = Rating.objects.filter(user=self.object).annotate(
            #     user_rate=Subquery(newest.values('rate')[:1])).select_related('title')
            ratings = Rating.objects.filter(user=self.object).extra(select={
                'user_rate': """SELECT rating.rate FROM titles_rating as rating
                WHERE rating.user_id = %s
                AND rating.title_id = titles_rating.title_id
                ORDER BY rating.rate_date DESC LIMIT 1""",
            }, select_params=[self.request.user.id])
            for r in ratings:
                print(r.user_rate)
        else:
            ratings = Rating.objects.filter(user=self.object).select_related('title')

        context.update({
            'is_owner': self.is_owner,
            'rating_list': ratings[:self.titles_in_a_row],
            # 'common_with_req_user': self.common
        })
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if self.request.POST.get('confirm-nick'):
            if self.request.POST['confirm-nick'] == self.request.user.username:
                deleted_count = Rating.objects.filter(user=self.request.user).delete()[0]
                message = 'You have deleted your {} ratings'.format(deleted_count)
            else:
                message = 'Confirmation failed. Wrong username. No ratings deleted.'
            messages.info(self.request, message, extra_tags='safe')
        elif self.is_owner:
            message = ''
            if self.request.POST.get('update_csv'):
                message = update_ratings_using_csv(self.object)
            elif self.request.POST.get('update_rss') and self.object.imdb_id:
                message = update_ratings(self.object)
            elif self.request.POST.get('update_watchlist') and self.object.imdb_id:
                message = update_watchlist(self.object)
            messages.info(self.request, message, extra_tags='safe')
        return redirect(self.object)

    def get_ratings_comparision(self):
        """
        gets additional context for a user who visits somebody else's profile
        """
        if self.user_ratings.count() > 0 and self.is_other_user:
            titles_req_user_rated_higher = titles_rated_higher_or_lower(
                self.object.id, self.request.user.id, sign='<', limit=self.titles_in_a_row)
            titles_req_user_rated_lower = titles_rated_higher_or_lower(
                self.object.id, self.request.user.id, sign='>', limit=self.titles_in_a_row)

            # title = Rating.objects.filter(user=request.user).filter(user=user.id)

            common_titles_avgs = avgs_of_2_users_common_curr_ratings(self.object.id, self.request.user.id)
            common_ratings_len = common_titles_avgs['count']

            not_rated_by_req_user = Title.objects.filter(rating__user=self.object, rating__rate__gte=7).only(
                'name', 'const').exclude(rating__user=self.request.user).distinct().extra(select={
                    'user_rate': """SELECT rate FROM movie_rating as rating
                        WHERE rating.title_id = movie_title.id
                        AND rating.user_id = %s
                        ORDER BY rating.rate_date DESC LIMIT 1"""
                }, select_params=[self.object.id])

            return {
                'count': common_ratings_len,
                'higher': titles_req_user_rated_higher,
                'lower': titles_req_user_rated_lower,
                'percentage': round(common_ratings_len / self.object.count_titles, 2) * 100,
                'user_rate_avg': common_titles_avgs['avg_user'],
                'req_user_rate_avg': common_titles_avgs['avg_req_user'],
                'not_rated_by_req_user': not_rated_by_req_user[:self.titles_in_a_row],
                'not_rated_by_req_user_count': Title.objects.filter(rating__user=self.object).exclude(
                    rating__user=self.request.user).distinct().count()
            }
        return {}
