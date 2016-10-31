from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from .forms import RegisterForm, LoginForm, EditProfileForm
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import UserProfile, UserFollow


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
        if request.POST.get('login_after') == 'on':
            created_user = auth.authenticate(username=user.username, password=request.POST.get('password'))
            auth.login(request, created_user)
            message += '. You have been logged in'
        messages.success(request, '{}, {}'.format(message, user.username), extra_tags='alert-success')
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
                messages.success(request, 'You have been logged in: ' + user.username, extra_tags='alert-success')
                return redirect(reverse('home'))
            else:
                messages.error(request, 'User not active', extra_tags='alert-warning')
        else:
            messages.error(request, 'Invalid creditentials', extra_tags='alert-warning')
    context = {
        'form': form,
        'title': 'login'
    }
    return render(request, 'users/login.html', context)

# from django.contrib.auth.decorators import login_required
# @login_required
def user_edit(request, username):
    if not request.user.username == username:
        messages.info(request, 'You can edit only your profile', extra_tags='alert-info')
        return redirect(reverse('user_profile', kwargs={'username': username}))
    profile = UserProfile.objects.get(user__username=username)
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
    messages.success(request, 'You have been logged out: ' + request.user.username, extra_tags='alert-success')
    return redirect(request.META.get('HTTP_REFERER'))


def user_list(request):
    list_of_users = User.objects.exclude(username=request.user.username) if request.user.is_authenticated() else User.objects.all()
    context = {
        'title': 'User list',
        'user_list': list_of_users,
    }
    return render(request, 'users/user_list.html', context)


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        if not request.user.is_authenticated():
            messages.error(request, 'You must be logged in to follow somebody')
            return redirect(reverse('user_profile', kwargs={'username': username}))

        if request.POST.get('follow'):
            UserFollow.objects.create(user_follower=request.user, user_followed=user)
        elif request.POST.get('unfollow'):
            UserFollow.objects.filter(user_follower=request.user, user_followed=user).delete()
        return redirect(reverse('user_profile', kwargs={'username': username}))

    can_follow = not UserFollow.objects.filter(user_follower=request.user, user_followed=user).exists()\
        if request.user.is_authenticated() else None
    context = {
        'title': 'User profile: ' + user.username,
        'choosen_user': user,
        'is_owner': user == request.user,
        'can_follow': can_follow,
    }
    return render(request, 'users/user_profile.html', context)


def notifications(request):
    return 1