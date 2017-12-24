from functools import reduce
from operator import and_
from os.path import splitext

from django.core.exceptions import ValidationError


class SearchFormMixin:
    """Mixin for forms used for searching. It works with views that inherit SearchViewMixin"""

    def search(self, queryset):
        if self.is_valid():
            search_queries = []
            for search_key, search_value in self.cleaned_data.items():
                print('cleaned:', search_key, search_value)
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
                print('queries:', search_queries)
                return queryset.filter(reduce(and_, search_queries))

        return queryset


class SizeExtValidatorMixin:

    @staticmethod
    def validate_size(file_size, max_size_in_kb):
        """raises ValidationError if file_size is bigger than max_size"""
        if file_size > max_size_in_kb * 1024:
            raise ValidationError(
                f'Maximum file size is {max_size_in_kb} kB. '
                f'Uploaded file\'s size is {round(float(file_size / 1024), 2)} kB'
            )

    @staticmethod
    def validate_extension(file_name, allowed_extensions):
        ext = splitext(file_name)[1]
        if ext not in allowed_extensions:
            raise ValidationError(f'Allowed file extensions: {", ".join(allowed_extensions)}.')
