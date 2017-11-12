class SearchViewMixin:
    """Mixin that adds search_form to context and calls search method. Form must inherit from SearchFormMixin"""

    search_form = None
    search_form_class = None

    def dispatch(self, request, *args, **kwargs):
        self.search_form = self.search_form_class(self.request.GET or None)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.search_form.search(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.search_form
        return context