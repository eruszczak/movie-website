from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect


class MessageMixin:
    # can check hasattr(self, 'request') and dialog. in __init__?
    def set_success_message(self):
        messages.warning(self.request, self.get_success_message())

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
        return redirect(self.request.user.userprofile)


class AuthLogoutView(MessageMixin, LogoutView):

    dialogs = {
        'success': 'You have been logged out, {}'
    }

    def get_next_page(self):
        self.set_success_message()
        return redirect(self.request.META.get('HTTP_REFERER'))

