from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView


# permission - not logged
# is_active is checked?
class AuthLoginView(LoginView):
    template_name = 'users/login.html'

    dialogs = {
        'success': 'You have been logged in, '
    }

    def get_success_url(self):
        messages.warning(self.request, self.dialogs['success'].format(self.request.username))
        return self.request.user.userprofile.get_absolute_url()
