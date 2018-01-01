from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class LoginRequiredMixin:

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class CacheMixin:
    cache_timeout = 60 * 60 * 24  # 24h

    def dispatch(self, *args, **kwargs):
        # don't cache for logged in users
        if self.request.user.is_authenticated:
            return super().dispatch(*args, **kwargs)
        return cache_page(self.cache_timeout)(super(CacheMixin, self).dispatch)(*args, **kwargs)
