from rest_framework.pagination import PageNumberPagination

class DefaultPageSize(PageNumberPagination):
    page_query_param = 'p'
    page_size = 2  # items per page
    # page_size_query_param = 'page_size'  # allow ?page_size=20 in URL
    # max_page_size = 100