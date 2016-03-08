import math
import pysolr
from rest_framework.utils.urls import replace_query_param
from rest_framework.reverse import reverse
from django.conf import settings
from collections import OrderedDict


class SolrResultObject(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)


class SolrResultException(BaseException):
    pass


class SolrPaginator:
    """
        Takes in a SolrSearch object (pre-execute) and manages
        a paginated list of Solr results.
    """
    def __init__(self, query, filters, sorts, request, *args, **kwargs):
        # The query is the value of the fulltext q-field.
        self.query = query
        self.request = request
        self.result = None

        # qopts are the query options passed to solr.
        self.qopts = {
            'q.op': settings.SOLR['DEFAULT_OPERATOR'],
            'facet': 'true',
            'facet.field': 'type',
            'facet.mincount': 1,
            'hl': 'true'
        }

        if sorts:
            self.qopts.update(sorts)

        if filters:
            fqstring = ""
            for k, v in filters.items():
                # If a list is passed in for a field, assume that we want to OR the filters to produce a listing from
                # all the values; if not, assume it's a restriction.
                # For example, {type: ['foo', 'bar']} ==> "type:foo OR type:bar"
                # but {type: 'foo'} ==> 'type:foo'
                if isinstance(v, list):
                    fqstring += " OR ".join(["{0}:{1}".format(k, field) for field in v])
                else:
                    fqstring += "{0}:{1} ".format(k, v)

            print(fqstring)
            self.qopts.update({
                'fq': fqstring
            })

            # fqstring = " ".join(["{0}:{1}".format(k, v) for k, v in filters.items()])
            # self.qopts.update({
            #     'fq': fqstring
            # })

        self.solr = pysolr.Solr(settings.SOLR['SERVER'])

        # Fetch the requested page.
        self._fetch_page()

    @property
    def page_size(self):
        return settings.SOLR['PAGE_SIZE']

    @property
    def count(self):
        if not self.result:
            return 0

        return int(self.result.hits)

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
        self.qopts.update({
            'start': start,
            'rows': settings.SOLR['PAGE_SIZE']
        })

        try:
            self.result = self.solr.search(self.query, **self.qopts)
        except pysolr.SolrError as e:
            raise SolrResultException(repr(e))

    def page(self, page_num=1):
        """
            page_num must be an integer. Do not pass in un-coerced request parameters!
        """
        # e.g., page 3: ((3 - 1) * 20) + 1, start = 41
        # remainder = 0 if page_num == 1 else 1  # page 1 starts at result 0; page 2 starts at result 11
        start = ((page_num - 1) * self.page_size)
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

        return OrderedDict([
            ('count', self.paginator.count),
            ('pagination', self.pagination),
            ('query', self.paginator.query),
            ('types', self.type_list),
            ('results', self.object_list),
        ])

    @property
    def type_list(self):
        # Takes a list of facets ['foo', 1, 'bar', 2] and converts them to
        # {'foo': 1, 'bar': 2} using some stupid python iterator tricks.
        facets = self.result.facets['facet_fields']['type']

        if not facets:
            return {}

        i = iter(facets)
        # Since Solr doesn't filter by facet _value_, we remove some of the values that we don't want
        # to display in the search results.
        filtered_facets = [k for k in sorted(zip(i, i), key=lambda f: f[0]) if k[0] in settings.SOLR['SEARCH_TYPES']]
        return OrderedDict(filtered_facets)

    @property
    def object_list(self):
        docs = self.result.docs
        highlights = self.result.highlighting
        # Generate fully qualified URLs for the resources in Solr when the results are returned.
        # This way we don't have to store the full URL in Solr.
        for obj in docs:
            # Filter out any result objects that are not of the type we want to display
            url = reverse("{0}-detail".format(obj['type']),
                          kwargs={'pk': obj['pk']},
                          request=self.paginator.request)
            obj['url'] = url

            hl = highlights.get(obj['id'], None)
            if hl:
                obj['result_text'] = "; ".join(hl['text'])

        return docs

    @property
    def pagination(self):
        pages = {}
        for pnum in range(self.paginator.num_pages):
            url = self.paginator.request.build_absolute_uri()
            pg_url = replace_query_param(url, 'page', pnum + 1)
            pages[pnum + 1] = pg_url

        return OrderedDict([
            ('next', self.next_url),
            ('previous', self.previous_url),
            ('current_page', self.number),
            ('num_pages', self.paginator.num_pages),
            ('pages', pages)
        ])

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
