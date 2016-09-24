from django.shortcuts import render, redirect
from django.contrib import auth, messages
from .forms import RegisterForm, LoginForm
from django.core.urlresolvers import reverse


def register(request):
    form_data = request.POST if request.method == 'POST' else None
    form = RegisterForm(form_data)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        message = 'Successful registration'
        if request.POST.get('login_after') == 'on':
            created_user = auth.authenticate(username=user.username, password=password)
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

    return render(request, 'users/login.html', {'form': form})


def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out: ' + request.user.username, extra_tags='alert-success')
    return redirect(request.META.get('HTTP_REFERER'))
