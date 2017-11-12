from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
    # PasswordChangeView as BasePasswordChangeView
)
from django.views.generic import CreateView

from accounts.forms import RegisterForm

User = get_user_model()


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    # redirect_authenticated_user = False

    def get_success_url(self):
        messages.warning(self.request, 'Welcome, {}.'.format(self.request.user.username))
        return self.request.user.get_absolute_url()


class LogoutView(BaseLogoutView):
    next_page = 'home'

    def get_next_page(self):
        messages.warning(self.request, 'You have been logged out.')
        return super().get_next_page()


class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm

    def get_success_url(self):
        messages.warning(self.request, 'Account created, {}. You are now logged in.'.format(self.object.username))
        return self.object.get_absolute_url()

    def form_valid(self, form):
        valid = super().form_valid(form)
        login(self.request, self.object)
        return valid


# class PasswordChangeView(BasePasswordChangeView):
#     template_name = 'accounts/password_change.html'
#     extra_context = {
#         'page_title': 'Change your password'
#     }
#
#     dialogs = {
#         'success': 'Password changed.'
#     }
#
#     def get_success_url(self):
#         self.set_success_message(attach_username=False)
#         return self.request.user.get_absolute_url()
