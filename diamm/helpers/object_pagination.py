from collections import OrderedDict
import re

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

class ObjectPagination(PageNumberPagination):
    def replace_page_query(self, url, page_num):
        regex = "(?P<prefix>&|\?)page=[0-9]+"
        if re.search(regex, url):
            return re.sub(regex, "\g<prefix>page=%d" % page_num, url)
        else:
            prefix = "&" if url.count("?") else "?"
            return ("%s%spage=%d" % (url, prefix, page_num))

    def get_paginated_response(self, data):
        base_url = self.request.build_absolute_uri()
        url = base_url[:base_url.find("?")]
        pages = dict((i, self.replace_page_query(base_url, i)) for i in range(1, self.page.paginator.num_pages + 1))

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
