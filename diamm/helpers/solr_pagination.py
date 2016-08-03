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
            'facet.field': settings.SOLR['FACET_FIELDS'] + settings.SOLR['GEO_FACETS'],
            'facet.limit': 10,
            'facet.mincount': 1,
            'facet.pivot': settings.SOLR['FACET_PIVOTS'],
            'hl': 'true',
            'defType': 'edismax',
            'qf': settings.SOLR['FULLTEXT_QUERYFIELDS']
        }

        if sorts:
            self.qopts.update(sorts)

        if filters:
            fqlist = list()
            for k, v in filters.items():
                # If a list is passed in for a field, assume that we want to OR the filters to produce a listing from
                # all the values; if not, assume it's a restriction.
                # For example, {type: ['foo', 'bar']} ==> "type:foo OR type:bar"
                # but {type: 'foo'} ==> 'type:foo'
                if isinstance(v, list):
                    fqlist.append(" OR ".join(["{0}:{1}".format(k, field) for field in v]))
                # Do a similar transform if the key is a tuple;
                # {(archive_country_s, country_s): 'Spain'} ==> "archive_country_s:Spain OR country_s:Spain"
                elif isinstance(k, tuple):
                    fqlist.append(" OR ".join(["{0}:{1}".format(key, v) for key in k]))
                else:
                    fqlist.append("{0}:{1}".format(k, v))

            self.qopts.update({
                'fq': fqlist
            })

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
            ('geo', self.geo_list),
            ('genres', self.genres_list),
            ('dates', self.century_list),
            ('results', self.object_list),
        ])

    @property
    def century_list(self):
        q_params = self.paginator.request.query_params
        query_string = "&".join(["{0}={1}".format(k, v) for k, v in q_params.items()])

        def facet_url(century):
            return "{0}?{1}&century={2}".format(reverse('search'), query_string, century)

        dates = self.result.facets['facet_pivot'].get('start_date_i,end_date_i')

        if not dates:
            return []

        #    [{'value': 1400, 'count': 25, 'pivot':
        #    [{'value': 1500', 'count': 20}]}, {'value': 1600', 'count': 5}]
        # => [{'name': 1400, 'count': 25, 'url': 'search/?century=1400'},
        #     {'name': 1500, 'count': 20, 'url': 'search/?century=1500'}
        d = {}
        for start_date in dates:
            for end_date in start_date['pivot']:
                s = start_date['value']
                while s < end_date['value']:
                    d[s] = d[s] + end_date['count'] if s in d else end_date['count']
                    s += 100

        return sorted(
            [{'name': k, 'count': v, 'url': facet_url(k)} for k, v in d.items()],
            key=lambda x: x['count'],
            reverse=True)

    @property
    def genres_list(self):
        q_params = self.paginator.request.query_params
        query_string = "&".join(["{0}={1}".format(k, v) for k, v in q_params.items()])

        def facet_url(genre):
            return "{0}?{1}&genre={2}".format(reverse('search'), query_string, genre)

        genres = self.result.facets['facet_fields'].get('genres_ss')
        if not genres:
            return []
        i = iter(genres)
        return [{'name': k, 'count': v, 'url': facet_url(k)} for k, v in zip(i, i)]

    @property
    def geo_list(self):
        q_params = self.paginator.request.query_params
        q_params = {k:v for k, v in q_params.items() if k not in ['country', 'city', 'archive']}
        query_string = "&".join(["{0}={1}".format(k, v) for k, v in q_params.items()])

        def facet_url(k, geo_type):
            return "{0}?{1}&{2}={3}".format(reverse('search'), query_string, geo_type, k)

        def reduce_list(l, geo_type):
            # Takes a list of facets ['foo', 1', 'bar' 2, 'bar', 1] and converts them to
            # [{'name': 'bar', 'count': 3, 'url': 'search/?country=bar'},
            #  {'name': 'foo', 'count': 1, 'url': 'search/?country=foo'}] where repeated keys have summed values
            if not l:
                return {}
            i = iter(l)
            d = {}
            for k, v in zip(i, i):
                d[k] = d[k] + v if k in d else v
            return sorted(
                [{'name': k, 'count': v, 'url': facet_url(k, geo_type)} for k, v in d.items()],
                key=lambda x: x['count'],
                reverse=True)

        facet_fields = self.result.facets['facet_fields']
        geo_dicts = {
            'country': reduce_list(
                facet_fields.get('archive_country_s') +
                facet_fields.get('country_s'),
                'country'),
            'city': reduce_list(
                facet_fields.get('archive_city_s') +
                facet_fields.get('city_s'),
                'city'),
            'archive': reduce_list(facet_fields.get('archive_s'), 'archive')
        }
        return geo_dicts

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

        # For the public_images_b facet, we will get the count for this value
        # and send it along with the sources_with_images key.
        image_count = self.result.facets['facet_fields'].get('public_images_b')
        if image_count:
            i = iter(image_count)
            d = dict(zip(i, i))
            if d.get('true'):
                filtered_facets.append(('sources_with_images', d['true']))

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
