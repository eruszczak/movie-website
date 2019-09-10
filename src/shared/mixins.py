from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class LoginRequiredMixin:

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class AnonymousCacheMixin:
    """view with this mixin will be cached for not logged users"""
    cache_timeout = 60 * 60 * 24  # 24h

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super().dispatch(*args, **kwargs)
        return cache_page(self.cache_timeout)(super().dispatch)(*args, **kwargs)
