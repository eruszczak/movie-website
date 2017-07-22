from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout

from .forms import RegisterForm
from .models import UserProfile


class MessageMixin:
    # can check hasattr(self, 'request') and dialog. in __init__?
    def set_success_message(self, attach_username=True, username=None):
        self.username = username or self.request.user.username
        msg = self.get_success_message_with_username() if attach_username else self.get_success_message()
        messages.warning(self.request, msg)

    def get_success_message_with_username(self):
        return self.dialogs['success'].format(self.username)

    def get_success_message(self):
        return self.dialogs['success']

    def get_message_level(self):
        raise NotImplementedError


# permission - not logged
# is_active is checked?
class AuthLoginView(MessageMixin, LoginView):
    template_name = 'users/login.html'
    extra_context = {
        'page_title': 'Login'
    }

    dialogs = {
        'success': 'Welcome, {}.'
    }

    def get_success_url(self):
        self.set_success_message()
        return self.request.user.userprofile.get_absolute_url()


# permission logged
class AuthLogoutView(MessageMixin, LogoutView):

    dialogs = {
        'success': 'You have been logged out, {}.'
    }

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        next_page = self.get_next_page()  # this must come first because I want to know username
        logout(request)
        if next_page:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(next_page)
        return super().dispatch(request, *args, **kwargs)

    def get_next_page(self):
        self.set_success_message()
        return reverse('home')


# permission logged
class AuthPasswordChangeView(MessageMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    extra_context = {
        'page_title': 'Change your password'
    }

    dialogs = {
        'success': 'Password changed.'
    }

    def get_success_url(self):
        self.set_success_message(attach_username=False)
        return self.request.user.userprofile.get_absolute_url()


class AuthRegisterView(MessageMixin, CreateView):
    template_name = 'users/register.html'
    form_class = RegisterForm

    dialogs = {
        'success': 'Account created, {}. You are now logged in.'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            'page_title': 'Register'
        })
        return context

    def get_success_url(self):
        """
        when form_valid() calls form.save() new User is created and signal is emitted and receiver creates its Profile
        so below I can query for that Profile and call its get_absolute_url so user is redirected to his profile
        """
        self.set_success_message(username=self.object.username)
        return UserProfile.objects.get(user=self.object).get_absolute_url()

    # def form_valid(self, form):
    #     pass