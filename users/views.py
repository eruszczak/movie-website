from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from .forms import RegisterForm, LoginForm, EditProfileForm
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import UserProfile, UserFollow
from common.prepareDB import update_from_csv, update_from_rss, get_watchlist
from common.utils import build_html_string_for_titles
from movie.models import Title, Rating
from django.utils import timezone


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
    if not request.user == profile.user:
        messages.info(request, 'You can edit only your profile')
        return redirect(profile)

    form = EditProfileForm(instance=profile)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
    context = {
        'form': form,
        'title': 'profile edit'
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
        users_who_saw_title = User.objects.filter(rating__title=title).distinct()
        users_who_saw_title = users_who_saw_title.extra(select={
            'current_rating': """SELECT rating.rate FROM movie_rating as rating, movie_title as title
                WHERE rating.title_id = title.id AND rating.user_id = auth_user.id AND title.id = %s LIMIT 1""",
            }, select_params=[title.id])
        context['users_who_saw_title'] = users_who_saw_title
        context['searched_title'] = title
    elif request.user.is_authenticated():
        list_of_users = User.objects.exclude(pk=request.user.pk)
        context['user_list'] = list_of_users
    else:
        list_of_users = User.objects.all()
        context['user_list'] = list_of_users
    return render(request, 'users/user_list.html', context)


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
        elif user == request.user:
            if request.POST.get('update_csv') and user.userprofile.csv_ratings:
                if user.userprofile.can_update_csv_ratings:
                    user.userprofile.last_updated_csv_ratings = timezone.now()
                    user.userprofile.save(update_fields=['last_updated_csv_ratings'])
                    updated_titles = update_from_csv(user)
                    message = None
                    if updated_titles:
                        message = '(csv) Updated {} titles: {}'.format(
                            len(updated_titles), build_html_string_for_titles(updated_titles))
                    if message is None:
                        message = 'Updated nothing using {}'.format(user.userprofile.csv_ratings)
                    messages.info(request, message, extra_tags='safe')
            elif request.POST.get('update_rss') and user.userprofile.imdb_id:
                if user.userprofile.can_update_rss_ratings:
                    user.userprofile.last_updated_rss_ratings = timezone.now()
                    user.userprofile.save(update_fields=['last_updated_rss_ratings'])
                    updated_titles = update_from_rss(user)
                    message = None
                    if updated_titles:
                        message = '(rss) Updated {} titles: {}'.format(
                            len(updated_titles), build_html_string_for_titles(updated_titles))
                    if message is None:
                        message = 'Updated nothing using <a href="http://rss.imdb.com/user/{}/ratings">RSS</a>'.format(
                            user.userprofile.imdb_id)
                    messages.info(request, message, extra_tags='safe')
            elif request.POST.get('update_watchlist') and user.userprofile.imdb_id:
                if user.userprofile.can_update_rss_watchlist:
                    user.userprofile.last_updated_rss_watchlist = timezone.now()
                    user.userprofile.save(update_fields=['last_updated_rss_watchlist'])
                    updated_titles, deleted_titles = get_watchlist(user)
                    message = None
                    if updated_titles:
                        message = '(rss watchlist) Updated {} titles: {}<br><br>Deleted {} titles: {}'.format(
                            len(updated_titles), build_html_string_for_titles(updated_titles),
                            len(deleted_titles), build_html_string_for_titles(deleted_titles))
                    if message is None:
                        message = 'Updated nothing using <a href="http://rss.imdb.com/user/{}/watchlist">RSS</a>'.format(
                            user.userprofile.imdb_id)
                    messages.info(request, message, extra_tags='safe')
        return redirect(user.userprofile)

    TITLES_SHOWED_IN_ROW = 5
    is_owner = user == request.user
    user_ratings = Rating.objects.filter(user=user)
    if request.user.is_authenticated() and not is_owner:
        common_ratings = Title.objects.filter(rating__user=request.user) & Title.objects.filter(rating__user=user)
        print(common_ratings.distinct())
        common_ratings = common_ratings.distinct().extra(select={
            'user_rate': """SELECT rate FROM movie_rating as rating
                WHERE rating.title_id = movie_title.id
                AND rating.user_id = %s
                ORDER BY rating.rate_date DESC LIMIT 1""",
            'req_user_rate': """SELECT rate FROM movie_rating as rating
                WHERE rating.title_id = movie_title.id
                AND rating.user_id = %s
                ORDER BY rating.rate_date DESC LIMIT 1""",
        }, select_params=[user.id, request.user.id])

        titles_req_user_rated_lower = []
        titles_req_user_rated_higher = []
        for title in common_ratings:
            higher_is_max_size = len(titles_req_user_rated_higher) > TITLES_SHOWED_IN_ROW
            lower_is_max_size = len(titles_req_user_rated_lower) > TITLES_SHOWED_IN_ROW
            if title.req_user_rate > title.user_rate and not higher_is_max_size:
                print(title.req_user_rate, title.user_rate, title)
                titles_req_user_rated_higher.append(title)
            elif title.req_user_rate < title.user_rate and not lower_is_max_size:
                titles_req_user_rated_lower.append(title)
            if lower_is_max_size and higher_is_max_size:
                break
        print(titles_req_user_rated_higher)
        print(titles_req_user_rated_lower)
        print(common_ratings)
        common = {
            'ratings': common_ratings,
            'count': common_ratings.count(),
            'higher': titles_req_user_rated_higher,
            'lower': titles_req_user_rated_lower,
            'percentage': int(common_ratings.count() / user_ratings.count() * 100)
        }
        can_follow = not UserFollow.objects.filter(user_follower=request.user, user_followed=user).exists()
    else:
        common = None
        can_follow = None
    context = {
        'title': 'User profile: ' + user.username,
        'choosen_user': user,
        'is_owner': is_owner,
        'can_follow': can_follow,
        'user_ratings': {
            'count': user_ratings.count(),
            'last_seen': user_ratings[:TITLES_SHOWED_IN_ROW],
            'common_with_req_user': common

        }
    }
    return render(request, 'users/user_profile.html', context)
