from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout


class MessageMixin:
    # can check hasattr(self, 'request') and dialog. in __init__?
    def set_success_message(self, attach_username=True):
        msg = self.get_success_message_with_username() if attach_username else self.get_success_message()
        messages.warning(self.request, msg)

    def get_success_message_with_username(self):
        return self.dialogs['success'].format(self.request.user.username)

    def get_success_message(self):
        return self.dialogs['success'].format(self.request.user.username)

    def get_message_level(self):
        raise NotImplementedError


# permission - not logged
# is_active is checked?
class AuthLoginView(MessageMixin, LoginView):
    template_name = 'users/login.html'
    extra_context = {
        'title': 'Login Page'
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

    dialogs = {
        'success': 'Password changed.'
    }

    def get_success_url(self):
        self.set_success_message(attach_username=False)
        return self.request.user.userprofile.get_absolute_url()
