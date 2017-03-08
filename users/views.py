from django.db.models import Count
from django.utils import timezone
from django.contrib import auth, messages
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from movie.models import Title, Rating
from .models import UserProfile, UserFollow
from .forms import RegisterForm, LoginForm, EditProfileForm
from common.utils import build_html_string_for_titles
from common.prepareDB import update_from_csv, update_from_rss, get_watchlist
from common.sql_queries import avgs_of_2_users_common_curr_ratings, titles_rated_higher_or_lower


def register(request):
    form_data = request.POST if request.method == 'POST' else None
    form = RegisterForm(form_data)
    if form.is_valid():
        user = form.save()
        user.set_password(user.password)
        user.save()
        profile = UserProfile()
        profile.user = user
        profile.save()
        message = 'Successful registration'
        if request.POST.get('login_after'):
            created_user = auth.authenticate(username=user.username, password=request.POST.get('password'))
            auth.login(request, created_user)
            message += '. You have been logged in'
        messages.success(request, '{}, {}'.format(message, user.username))
        return redirect(reverse('home'))
    return render(request, 'users/register.html', {'form': form})


def login(request):
    form_data = request.POST if request.method == 'POST' else None
    form = LoginForm(form_data)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth.login(request, user)
                messages.success(request, 'You have been logged in: ' + user.username)
                return redirect(reverse('home'))
            else:
                messages.warning(request, 'User not active')
        else:
            messages.warning(request, 'Invalid creditentials')
    context = {
        'form': form,
        'title': 'login'
    }
    return render(request, 'users/login.html', context)


def user_edit(request, username):
    profile = UserProfile.objects.get(user__username=username)
    if request.user != profile.user:
        messages.info(request, 'You can edit only your profile')
        return redirect(profile)

    form = EditProfileForm(instance=profile)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated')
            return redirect(profile)
        else:
            for field, message in form.errors.items():
                print(field, message)
            t = '\n'.join([message[0] for field, message in form.errors.items()])
            print(t)
            messages.warning(request, t)
        return redirect(request.META.get('HTTP_REFERER'))
    context = {
        'form': form,
        'title': 'profile edit',
        'profile': profile,
    }
    return render(request, 'users/profile_edit.html', context)


def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out: ' + request.user.username)
    return redirect(request.META.get('HTTP_REFERER'))


def user_list(request):
    context = {'title': 'User list'}
    if request.GET.get('s'):
        title = get_object_or_404(Title, slug=request.GET['s'])
        users_who_saw_title = User.objects.filter(rating__title=title).annotate(num=Count('rating__id')).distinct()
        users_who_saw_title = users_who_saw_title.extra(select={
            'current_rating': """SELECT rating.rate FROM movie_rating as rating, movie_title as title
                WHERE rating.title_id = title.id AND rating.user_id = auth_user.id AND title.id = %s
                ORDER BY rating.rate_date DESC LIMIT 1""",
            }, select_params=[title.id])

        context['user_list'] = users_who_saw_title.order_by('-num')[:30]
        context['searched_title'] = title
    else:
        list_of_users = User.objects.exclude(pk=request.user.pk).annotate(num=Count('rating__id')).order_by('-num')[:30]
        context['user_list'] = list_of_users
    return render(request, 'users/user_list.html', context)


def user_profile(request, username):
    msgs = {
        'updated': 'Used {}. Updated {} titles: {}.',
        'updated_nothing': 'Updated nothing using {}',
        'watchlist_updated': '(rss watchlist) Updated {} titles: {}',
        'watchlist_deleted': '{}Deleted {} titles: {}',
        'error': 'Problem with fetching data. IMDb may be down, you provided wrong IMDb Id or your list is private.',
        'timeout': 'Wait a few minutes'
    }

    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        if not request.user.is_authenticated():
            messages.error(request, 'You must be logged in to follow somebody')
            return redirect(user.userprofile)

        if request.POST.get('follow'):
            UserFollow.objects.create(user_follower=request.user, user_followed=user)
        elif request.POST.get('unfollow'):
            UserFollow.objects.filter(user_follower=request.user, user_followed=user).delete()
        elif user == request.user:
            if request.POST.get('update_csv') and user.userprofile.csv_ratings:
                if user.userprofile.can_update_csv_ratings:
                    user.userprofile.last_updated_csv_ratings = timezone.now()
                    user.userprofile.save(update_fields=['last_updated_csv_ratings'])
                    updated_titles, count = update_from_csv(user)
                    if updated_titles:
                        message = msgs['updated'].format(user.userprofile.csv_ratings.split('/')[-1],
                                                         count,
                                                         build_html_string_for_titles(updated_titles))
                    else:
                        message = msgs['updated_nothing'].format(user.userprofile.csv_ratings)
                else:
                    message = msgs['timeout']
                messages.info(request, message, extra_tags='safe')
            elif request.POST.get('update_rss') and user.userprofile.imdb_id:
                if user.userprofile.can_update_rss_ratings:
                    user.userprofile.last_updated_rss_ratings = timezone.now()
                    user.userprofile.save(update_fields=['last_updated_rss_ratings'])
                    data = update_from_rss(user)
                    if data is not None:
                        updated_titles, count = data
                        link = '<a href="http://rss.imdb.com/user/{}/ratings">ratings</a>'.format(
                            user.userprofile.imdb_id)
                        if updated_titles:
                            message = msgs['updated'].format(link, count, build_html_string_for_titles(updated_titles))
                        else:
                            message = msgs['updated_nothing'].format(link)
                    else:
                        message = msgs['error']
                else:
                    message = msgs['timeout']
                messages.info(request, message, extra_tags='safe')
            elif request.POST.get('update_watchlist') and user.userprofile.imdb_id:
                if user.userprofile.can_update_rss_watchlist:
                    user.userprofile.last_updated_rss_watchlist = timezone.now()
                    user.userprofile.save(update_fields=['last_updated_rss_watchlist'])
                    data = get_watchlist(user)
                    message = ''
                    if data is not None:
                        updated_titles, updated_titles_count = data['updated']
                        deleted_titles, deleted_titles_count = data['deleted']
                        link = '<a href="http://rss.imdb.com/user/{}/watchlist">watchlist</a>'.format(
                            user.userprofile.imdb_id)
                        if updated_titles:
                            message += msgs['updated'].format(link,
                                                              updated_titles_count,
                                                              build_html_string_for_titles(updated_titles))
                        if deleted_titles:
                            message += msgs['watchlist_deleted'].format('<br><br>' if message else '',
                                                                        deleted_titles_count,
                                                                        build_html_string_for_titles(deleted_titles))
                        if not message:
                            message = msgs['updated_nothing'].format(link)
                    else:
                        message = msgs['error']
                else:
                    message = msgs['timeout']
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

        common_titles_avgs = avgs_of_2_users_common_curr_ratings(user.id, request.user.id)
        common_ratings_len = common_titles_avgs['count']

        not_rated_by_req_user = Title.objects.filter(rating__user=user, rating__rate__gte=7).exclude(
            rating__user=request.user).distinct().extra(select={
                'user_rate': """SELECT rate FROM movie_rating as rating
                WHERE rating.title_id = movie_title.id
                AND rating.user_id = %s
                ORDER BY rating.rate_date DESC LIMIT 1"""
            }, select_params=[user.id])

        if user_ratings.count() > 0:
            common = {
                'count': common_ratings_len,
                'higher': titles_req_user_rated_higher,
                'lower': titles_req_user_rated_lower,
                'percentage': int(common_ratings_len / user.userprofile.count_ratings * 100),
                'user_rate_avg': common_titles_avgs['avg_user'],
                'req_user_rate_avg': common_titles_avgs['avg_req_user'],
                'not_rated_by_req_user': not_rated_by_req_user[:titles_in_a_row],
                'not_rated_by_req_user_count': Title.objects.filter(rating__user=user).exclude(
                    rating__user=request.user).distinct().count()
            }
        else:
            common = {}
        can_follow = not UserFollow.objects.filter(user_follower=request.user, user_followed=user).exists()
    else:
        common = None
        can_follow = False
        user_ratings = Rating.objects.filter(user=user)

    context = {
        'title': user.username + ' | profile',
        'choosen_user': user,
        'is_owner': is_owner,
        'can_follow': can_follow,
        'user_ratings': {
            'last_seen': user_ratings[:titles_in_a_row],
            'common_with_req_user': common
        }
    }
    return render(request, 'users/user_profile.html', context)
