from functools import reduce
from operator import and_


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


class SearchFormMixin:
    """Mixin for forms used for searching. It works with views that inherit SearchViewMixin"""

    def search(self, queryset):
        if self.is_valid():
            search_queries = []
            for search_key, search_value in self.cleaned_data.items():
                if not search_value:
                    continue

                try:
                    search_method = getattr(self, 'search_{}'.format(search_key))
                except AttributeError:
                    continue

                query = search_method(search_value)
                search_queries.append(query)

            if search_queries:
                return queryset.filter(reduce(and_, search_queries))

        return queryset