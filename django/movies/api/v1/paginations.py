from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MoviesApiPagination(PageNumberPagination):
    """Pagination class for movies class."""

    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'prev': self.page.previous_page_number() if self.get_previous_link() else None,
            'next': self.page.next_page_number() if self.get_next_link() else None,
            'results': data,
        })
