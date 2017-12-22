from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
    # PasswordChangeView as BasePasswordChangeView
)
from django.urls import reverse
from django.views.generic import CreateView

from accounts.forms import RegisterForm

User = get_user_model()


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    # redirect_authenticated_user = False

    def get_success_url(self):
        messages.warning(self.request, 'Welcome, {}.'.format(self.request.user.username))
        if self.request.GET.get('next'):
            return self.request.GET['next']

        return self.request.user.get_absolute_url()


class LogoutView(BaseLogoutView):
    next_page = 'home'

    def get_next_page(self):
        messages.warning(self.request, 'You have been logged out.')
        next_page = self.request.GET.get('next')
        if next_page:
            return next_page
        return super().get_next_page()


class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    login_after = False

    def get_success_url(self):
        messages.warning(self.request, 'Account created.')
        if self.request.GET.get('next'):
            return self.request.GET['next']

        if self.login_after:
            return self.object.get_absolute_url()

        return reverse('login')

    def form_valid(self, form):
        self.login_after = form.cleaned_data.get('login_after')
        form_valid = super().form_valid(form)
        if self.login_after:
            login(self.request, self.object)
        return form_valid


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
