from functools import reduce
from operator import and_


class SearchFormMixin:
    """Mixin for forms used for searching. It works with views that inherit SearchViewMixin"""

    def search(self, queryset):
        if self.is_valid():
            search_queries = []
            for search_key, search_value in self.cleaned_data.items():
                print(search_key, search_value)
                if not search_value:
                    continue

                try:
                    search_method = getattr(self, 'search_{}'.format(search_key))
                except AttributeError:
                    continue

                query = search_method(search_value)
                search_queries.append(query)

            if search_queries:
                # flat_list = [item for sublist in search_queries for item in sublist]
                # print(flat_list)
                print(search_queries)
                return queryset.filter(reduce(and_, search_queries))

        return queryset


