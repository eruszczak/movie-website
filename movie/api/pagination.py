from rest_framework.pagination import PageNumberPagination


class SetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'per_page'
