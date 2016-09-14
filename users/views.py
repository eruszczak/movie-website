from django.shortcuts import render, redirect
from django.contrib import auth, messages
from .forms import UserForm


def register(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
    else:
        user_form = UserForm()
    context = {
        'form': user_form,
    }
    return render(request, 'users/register.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth.login(request, user)
                messages.success(request, 'You have been logged in: ' + user.username, extra_tags='alert-success')
                return redirect('/')
            else:
                messages.error(request, 'User not active', extra_tags='alert-warning')
        else:
            messages.error(request, 'Invalid creditentials', extra_tags='alert-warning')

    return render(request, 'users/login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out: ' + request.user.username, extra_tags='alert-success')
    return redirect('/')
