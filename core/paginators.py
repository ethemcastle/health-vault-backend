from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Paginator(PageNumberPagination):
    template = None
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    paginate_query_param = 'paginate'

    def paginate_queryset(self, queryset, request, view=None):
        paginate = request.query_params.get(self.paginate_query_param, 'true').lower()
        if paginate in ['false', '0', 'no']:
            return None

        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data: dict):
        data.update({
            'pagination': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'num_pages': self.page.paginator.num_pages,
            }
        })
        return Response(data)
