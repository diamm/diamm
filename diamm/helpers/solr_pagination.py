import math
from rest_framework.utils.urls import replace_query_param
from rest_framework.reverse import reverse
from django.core.paginator import PageNotAnInteger
from collections import OrderedDict


class SolrResultObject(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)


class SolrPaginator:
    """
        Takes in a SolrSearch object (pre-execute) and manages
        a paginated list of Solr results.
    """
    def __init__(self, query, request, *args, **kwargs):
        self.query = query
        self.request = request
        self.result = None

        # Fetch the first page.
        self._fetch_page()

    @property
    def page_size(self):
        return self.query.paginator.rows

    @property
    def count(self):
        if not self.result:
            return 0

        return int(self.result.result.numFound)

    @property
    def num_pages(self):
        if self.count == 0:
            return 0
        return int(math.ceil(float(self.count) / float(self.page_size)))

    @property
    def page_range(self):
        if self.count == 0:
            return []
        return list(range(1, self.num_pages + 1))

    def _fetch_page(self, start=0):
        """Retrieve a new result response from Solr."""
        self.query.paginator.update(start, 10)
        self.result = self.query.execute()

    def page(self, page_num=1):
        try:
            page_num = int(page_num)
        except ValueError:
            raise PageNotAnInteger

        start = (page_num - 1) * self.page_size
        self._fetch_page(start=start)

        return SolrPage(self.result, page_num, self)


class SolrPage:
    def __init__(self, result, page_num, paginator):
        self.result = result
        self.number = page_num
        self.paginator = paginator

    def get_paginated_response(self):
        """
            Returns a full response object
        """
        print(self.paginator.request)

        return OrderedDict([
            ('count', self.paginator.count),
            ('next', self.next_url),
            ('previous', self.previous_url),
            ('current_page', self.number),
            ('total_pages', self.paginator.num_pages),
            ('results', self.object_list)
        ])

    @property
    def object_list(self):
        docs = self.result.result.docs
        for obj in docs:
            url = reverse("{0}-detail".format(obj['type']),
                          kwargs={'pk': obj['pk']},
                          request=self.paginator.request)
            obj['url'] = url
        return docs

    @property
    def next_url(self):
        if not self.has_next:
            return None
        url = self.paginator.request.build_absolute_uri()
        page_number = self.next_page_number
        return replace_query_param(url, 'page', page_number)


    @property
    def previous_url(self):
        if not self.has_previous:
            return None
        url = self.paginator.request.build_absolute_uri()
        page_number = self.previous_page_number
        return replace_query_param(url, 'page', page_number)

    @property
    def has_next(self):
        return self.number < self.paginator.num_pages

    @property
    def has_previous(self):
        return self.number > 1

    @property
    def has_other_pages(self):
        return self.paginator.num_pages > 1

    @property
    def start_index(self):
        return (self.number - 1) * self.paginator.page_size

    @property
    def end_index(self):
        return self.start_index + len(self.result.docs) - 1

    @property
    def next_page_number(self):
        return self.number + 1

    @property
    def previous_page_number(self):
        return self.number - 1
