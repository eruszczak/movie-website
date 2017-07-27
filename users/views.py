import io
import csv
from datetime import datetime

from django.db.models import Count
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DetailView

from movie.models import Title, Rating
from users.models import UserProfile, UserFollow
from users.forms import EditProfileForm
from users.functions import (
    update_ratings_using_csv,
    update_ratings,
    update_watchlist,
    validate_imported_ratings,
    create_csv_with_user_ratings
)
from common.sql_queries import avgs_of_2_users_common_curr_ratings, titles_rated_higher_or_lower
from common.prepareDB_utils import validate_rate, convert_to_datetime


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
    profile = UserProfile.objects.get(user=request.user)
    uploaded_file = request.FILES['csv_ratings']
    file = uploaded_file.read().decode('utf-8')
    io_string = io.StringIO(file)
    is_valid, message = validate_imported_ratings(uploaded_file, io_string)
    if not is_valid:
        messages.info(request, message)
        return redirect(profile)

    # TODO make a class that handles serialization and deserialization
    reader = csv.DictReader(io_string)
    total_rows = 0
    created_count = 0
    for row in reader:
        total_rows += 1
        const, rate_date, rate = row['const'], row['rate_date'], row['rate']
        title = Title.objects.filter(const=const).first()
        rate_date = convert_to_datetime(row['rate_date'], 'exported_from_db')

        if title and validate_rate(rate) and rate_date:
            obj, created = Rating.objects.get_or_create(user=request.user, title=title, rate_date=rate_date,
                                                        defaults={'rate': rate})
            if created:
                created_count += 1
    messages.info(request, 'imported {} out of {} ratings'.format(created_count, total_rows))
    return redirect(profile)


# def user_edit(request, username):
#     profile =
#     if request.user != profile.user:
#         messages.info(request, 'You can edit only your profile')
#         return redirect(profile)
#
#     form = EditProfileForm(instance=profile)
#     if request.method == 'POST':
#         form = EditProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.warning(request, 'Profile updated')
#             return redirect(profile)
#         else:
#             t = '\n'.join([message[0] for field, message in form.errors.items()])
#             messages.warning(request, t)
#         return redirect(profile.edit_url())
#
#     profile.csv_ratings = str(profile.csv_ratings).split('/')[-1]
#     context = {
#         'form': form,
#         'title': 'profile edit, ' + username,
#         'profile': profile,
#         'profile_ratings_name': str(profile.csv_ratings).split('/')[-1]
#     }
#     return render(request, 'users/profile_edit.html', context)


# do i need object permissions (is_owner) if getting object by self.request? or just LoginRequired
class UserUpdateView(UpdateView):
    model = UserProfile
    form_class = EditProfileForm
    template_name = 'users/user_edit.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Update your profile'
        })
        return context


class UserListView(ListView):
    template_name = 'users/user_list2.html'
    paginate_by = 10
    searched_title = None

    def get_queryset(self):
        if self.request.GET.get('s'):
            self.searched_title = get_object_or_404(Title, slug=self.request.GET['s'])
            queryset = self.get_users_who_saw_a_title()
        else:
            queryset = User.objects.annotate(num=Count('rating')).order_by('-num', '-username')

        if self.request.user.is_authenticated:
            queryset = queryset.extra(select={
                'already_follows': """SELECT 1 FROM users_userfollow as followage
                    WHERE followage.user_follower_id = %s and followage.user_followed_id = auth_user.id""",
            }, select_params=[self.request.user.id])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'List of users'
        if self.searched_title:
            context.update({
                'searched_title': self.searched_title,
                'query_string': '?s=' + self.request.GET['s'] + '&page=',
                'page_title': 'Users who saw {}'.format(str(self.searched_title))
            })
        return context

    def get_users_who_saw_a_title(self):
        return User.objects.filter(rating__title=self.searched_title).distinct().extra(select={
            'current_rating': """SELECT rating.rate FROM movie_rating as rating, movie_title as title
                WHERE rating.title_id = title.id AND rating.user_id = auth_user.id AND title.id = %s
                ORDER BY rating.rate_date DESC LIMIT 1"""
        }, select_params=[self.searched_title.id]).order_by('-current_rating', '-username')


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user_profile2.html'
    url_lookup_kwarg = 'username'
    titles_in_a_row = 6
    is_owner = False  # checks if a request user is an owner of the profile
    can_follow = False
    common = None
    user_ratings = None
    is_other_user = False  # authenticated user who is not an owner of the profile

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.is_owner = self.object == self.request.user
        self.is_other_user = self.request.user.is_authenticated and not self.is_owner
        self.user_ratings = self.get_user_ratings()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        return self.model.objects.get(username=self.kwargs[self.url_lookup_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.is_other_user:
            self.can_follow = not UserFollow.objects.filter(
                user_follower=self.request.user, user_followed=self.object).exists()
            self.common = self.get_user_ratings()

        context.update({
            'page_title': 'Profile of {}'.format(self.object.username),
            'is_owner': self.is_owner,
            'can_follow': self.can_follow,
            'user_ratings': {
                'last_seen': self.user_ratings[:self.titles_in_a_row],
                'common_with_req_user': self.common
            }
        })
        return context

    def get_user_ratings(self):
        if self.is_other_user:
            return Rating.objects.filter(user=self.object).extra(select={
                'req_user_curr_rating': """SELECT rating.rate FROM movie_rating as rating
                WHERE rating.user_id = %s
                AND rating.title_id = movie_rating.title_id
                ORDER BY rating.rate_date DESC LIMIT 1""",
            }, select_params=[self.request.user.id])
        return Rating.objects.filter(user=self.object).select_related('title')

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

            not_rated_by_req_user = Title.objects\
                .filter(rating__user=self.object, rating__rate__gte=7)\
                .only('name', 'const')\
                .exclude(rating__user=self.request.user)\
                .distinct()\
                .extra(select={
                    'user_rate': """SELECT rate FROM movie_rating as rating
                        WHERE rating.title_id = movie_title.id
                        AND rating.user_id = %s
                        ORDER BY rating.rate_date DESC LIMIT 1"""
                }, select_params=[self.object.id])

            return {
                'count': common_ratings_len,
                'higher': titles_req_user_rated_higher,
                'lower': titles_req_user_rated_lower,
                'percentage': round(common_ratings_len / self.object.userprofile.count_titles, 2) * 100,
                'user_rate_avg': common_titles_avgs['avg_user'],
                'req_user_rate_avg': common_titles_avgs['avg_req_user'],
                'not_rated_by_req_user': not_rated_by_req_user[:self.titles_in_a_row],
                'not_rated_by_req_user_count': Title.objects.filter(rating__user=self.object).exclude(
                    rating__user=self.request.user).distinct().count()
            }
        return {}


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        if not request.user.is_authenticated():
            messages.error(request, 'You must be logged in to follow somebody')
            return redirect(user.userprofile)

        if request.POST.get('follow'):
            UserFollow.objects.create(user_follower=request.user, user_followed=user)
        elif request.POST.get('unfollow'):
            UserFollow.objects.filter(user_follower=request.user, user_followed=user).delete()
        elif request.POST.get('confirm-nick'):
            if request.POST['confirm-nick'] == request.user.username:
                deleted_count = Rating.objects.filter(user=request.user).delete()[0]
                message = 'You have deleted your {} ratings'.format(deleted_count)
            else:
                message = 'Confirmation failed. Wrong username. No ratings deleted.'
            messages.info(request, message, extra_tags='safe')
        elif user == request.user:
            message = ''
            if request.POST.get('update_csv'):
                message = update_ratings_using_csv(user)
            elif request.POST.get('update_rss') and user.userprofile.imdb_id:
                message = update_ratings(user)
            elif request.POST.get('update_watchlist') and user.userprofile.imdb_id:
                message = update_watchlist(user)
            messages.info(request, message, extra_tags='safe')

        return redirect(user.userprofile)

    titles_in_a_row = 6
    is_owner = user == request.user

    if request.user.is_authenticated() and not is_owner:
        user_ratings = Rating.objects.filter(user=user).extra(select={
            'req_user_curr_rating': """SELECT rating.rate FROM movie_rating as rating
            WHERE rating.user_id = %s
            AND rating.title_id = movie_rating.title_id
            ORDER BY rating.rate_date DESC LIMIT 1""",
        }, select_params=[request.user.id])

        titles_req_user_rated_higher = titles_rated_higher_or_lower(
            user.id, request.user.id, sign='<', limit=titles_in_a_row)
        titles_req_user_rated_lower = titles_rated_higher_or_lower(
            user.id, request.user.id, sign='>', limit=titles_in_a_row)

        # title = Rating.objects.filter(user=request.user).filter(user=user.id)

        common_titles_avgs = avgs_of_2_users_common_curr_ratings(user.id, request.user.id)
        common_ratings_len = common_titles_avgs['count']

        not_rated_by_req_user = Title.objects.filter(rating__user=user, rating__rate__gte=7).only('name', 'const').exclude(
            rating__user=request.user).distinct().extra(select={
                'user_rate': """SELECT rate FROM movie_rating as rating
                WHERE rating.title_id = movie_title.id
                AND rating.user_id = %s
                ORDER BY rating.rate_date DESC LIMIT 1"""
            }, select_params=[user.id])

        common = {}
        if user_ratings.count() > 0:
            common = {
                'count': common_ratings_len,
                'higher': titles_req_user_rated_higher,
                'lower': titles_req_user_rated_lower,
                'percentage': round(common_ratings_len / user.userprofile.count_titles, 2) * 100,
                'user_rate_avg': common_titles_avgs['avg_user'],
                'req_user_rate_avg': common_titles_avgs['avg_req_user'],
                'not_rated_by_req_user': not_rated_by_req_user[:titles_in_a_row],
                'not_rated_by_req_user_count': Title.objects.filter(rating__user=user).exclude(
                    rating__user=request.user).distinct().count()
            }
        can_follow = not UserFollow.objects.filter(user_follower=request.user, user_followed=user).exists()
    else:
        common = None
        can_follow = False
        user_ratings = Rating.objects.filter(user=user).select_related('title')

    context = {
        'page_title': '{} profile'.format(user.username),
        'profile_owner': user,
        'is_owner': is_owner,
        'can_follow': can_follow,
        'user_ratings': {
            'last_seen': user_ratings[:titles_in_a_row],
            'common_with_req_user': common
        }
    }
    return render(request, 'users/user_profile.html', context)
