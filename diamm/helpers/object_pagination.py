import re
from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.utils.urls import replace_query_param


class ObjectPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        base_url = self.request.build_absolute_uri()
        url = base_url[:base_url.find("?")]
        pages = dict((i, replace_query_param(base_url, 'page', i)) for i in range(1, self.page.paginator.num_pages + 1))

        return Response(OrderedDict([
            ('results', data),
            ('count', self.page.paginator.count),
            ('url', url),
            ('pagination', {
                'current_page': self.page.number,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'num_pages': self.page.paginator.num_pages,
                'pages': pages
            })
        ]))
