"""
Pagination classes for Django REST Framework.
"""

from rest_framework.pagination import PageNumberPagination


class PageNumberPagination(PageNumberPagination):
    """
    Custom pagination class with configurable page size.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return a paginated response with additional metadata.
        """
        return {
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'page_size': self.page_size,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages
        }
