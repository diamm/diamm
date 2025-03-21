import math
from collections import OrderedDict

import pysolr
import serpy
from django.conf import settings
from rest_framework.reverse import reverse
from rest_framework.utils.urls import replace_query_param

from diamm.helpers.solr_helpers import SolrConnection
from diamm.serializers.serializers import ContextDictSerializer


class SolrResultObject:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class SolrResultSerializer(ContextDictSerializer):
    pk = serpy.StrField(attr="pk")
    url = serpy.MethodField()
    heading = serpy.MethodField()
    res_type = serpy.StrField(attr="type", label="type")
    display_name = serpy.StrField(attr="display_name_s", required=False)
    shelfmark = serpy.StrField(attr="shelfmark_s", required=False)
    archive_name = serpy.StrField(attr="archive_s", required=False)
    archive_city = serpy.StrField(attr="archive_city_s", required=False)
    surface = serpy.StrField(attr="surface_type_s", required=False)
    source_type = serpy.StrField(attr="source_type_s", required=False)
    date_statement = serpy.StrField(attr="date_statement_s", required=False)
    measurements = serpy.StrField(attr="measurements_s", required=False)
    inventory_provided = serpy.BoolField(attr="inventory_provided_b", required=False)
    number_of_compositions = serpy.IntField(
        attr="number_of_compositions_i", required=False
    )
    number_of_composers = serpy.IntField(attr="number_of_composers_i", required=False)
    notations = serpy.Field(attr="notations_ss", required=False)
    start_date = serpy.IntField(attr="start_date_i", required=False)
    end_date = serpy.IntField(attr="end_date_i", required=False)
    public_images = serpy.BoolField(attr="public_images_b", required=False)
    name = serpy.StrField(attr="name_s", required=False)
    location = serpy.StrField(attr="location_s", required=False)
    title = serpy.StrField(attr="title_s", required=False)
    composers = serpy.Field(attr="composers_ss", required=False)
    siglum = serpy.StrField(attr="siglum_s", required=False)
    city = serpy.StrField(attr="city_s", required=False)
    country = serpy.StrField(attr="country_s", required=False)
    cluster_shelfmark = serpy.StrField(attr="cluster_shelfmark_s", required=False)
    archives = serpy.Field(attr="archives_ss", required=False)
    sources = serpy.MethodField()

    def get_url(self, obj: dict) -> str:
        return reverse(
            f"{obj.get('type')}-detail",
            kwargs={"pk": obj.get("pk")},
            request=self.context.get("request"),
        )

    def get_heading(self, obj: dict) -> str:
        if obj.get("display_name_s"):
            return obj.get("display_name_s")
        elif obj.get("name_s"):
            return obj.get("name_s")
        elif obj.get("title_s"):
            return obj.get("title_s")
        elif obj.get("cluster_shelfmark_s"):
            return obj.get("cluster_shelfmark_s")
        else:
            return "[Unknown Heading]"

    def get_sources(self, obj: dict) -> int | None:
        if obj.get("sources_ii"):
            return len(obj.get("sources_ii"))
        return None


class SolrResultException(BaseException):
    pass


class PageRangeOutOfBoundsException(BaseException):
    pass


class SolrPaginator:
    """
    Takes in a SolrSearch object (pre-execute) and manages
    a paginated list of Solr results.
    """

    def __init__(
        self, query, filters, exclusive_filters, sorts, request, *args, **kwargs
    ):
        # The query is the value of the fulltext q-field.
        self.query = query
        self.request = request
        self.result = None
        self.absolute_uri = request.build_absolute_uri()

        # qopts are the query options passed to solr.
        self.qopts = {
            "q.op": settings.SOLR["DEFAULT_OPERATOR"],
            "facet": "true",
            "facet.field": settings.SOLR["FACET_FIELDS"],
            "facet.mincount": 1,
            "facet.limit": -1,
            "json.nl": "arrmap",
            "facet.pivot": settings.SOLR["FACET_PIVOTS"],
            "hl": "true",
            "defType": "edismax",
            "qf": settings.SOLR["FULLTEXT_QUERYFIELDS"],
            "bq": ["type:source^10", "type:archive^5", "type:person^1"],
        }
        self.qopts.update(settings.SOLR["FACET_SORT"])

        if sorts:
            self.qopts["sort"] = sorts

        fqlist = []

        if filters:
            for k, v in filters.items():
                # If a list is passed in for a field, assume that we want to OR the filters to produce a listing from
                # all the values; if not, assume it's a restriction.
                # For example, {type: ['foo', 'bar']} ==> "type:foo OR type:bar"
                # but {type: 'foo'} ==> 'type:foo'
                if isinstance(v, list):
                    fqlist.append(" OR ".join([f"{k}:{field}" for field in v]))
                else:
                    fqlist.append(f"{k}:{v}")

        if exclusive_filters:
            for k, v in exclusive_filters.items():
                # unlike the previous filters, this will be ANDed and not ORed
                if isinstance(v, list):
                    fqlist.append(" AND ".join([f"{k}:{field}" for field in v]))
                else:
                    fqlist.append(f"{k}:{v}")

        # update our fq query opts with the values from our filters.
        self.qopts.update({"fq": fqlist})

        # self.solr = pysolr.Solr(settings.SOLR['SERVER'])

        # Fetch the requested page.
        self._fetch_page()

    @property
    def page_size(self):
        return settings.SOLR["PAGE_SIZE"]

    @property
    def count(self) -> int:
        if not self.result:
            return 0

        return int(self.result.hits)

    @property
    def num_pages(self) -> int:
        if self.count == 0:
            return 0
        return int(math.ceil(float(self.count) / float(self.page_size)))

    @property
    def page_range(self) -> list:
        if self.count == 0:
            return []
        return list(range(1, self.num_pages + 1))

    def _fetch_page(self, start=0):
        """Retrieve a new result response from Solr."""
        self.qopts.update({"start": start, "rows": settings.SOLR["PAGE_SIZE"]})

        try:
            self.result = SolrConnection.search(self.query, **self.qopts)
        except pysolr.SolrError as e:
            raise SolrResultException(repr(e)) from e

    def page(self, page_num=1):
        """
        page_num must be an integer. Do not pass in un-coerced request parameters!
        """
        # e.g., page 3: ((3 - 1) * 20) + 1, start = 41
        # remainder = 0 if page_num == 1 else 1  # page 1 starts at result 0; page 2 starts at result 11
        if self.num_pages != 0 and page_num > self.num_pages:
            raise PageRangeOutOfBoundsException()

        start = (page_num - 1) * self.page_size
        self._fetch_page(start=start)
        return SolrPage(self.result, page_num, self)


class SolrPage:
    def __init__(self, result, page_num, paginator):
        self.result = result
        self.number = page_num
        self.paginator = paginator

    def get_paginated_response(self) -> dict:
        """
        Returns a full response object
        """

        return OrderedDict(
            [
                ("count", self.paginator.count),
                ("pagination", self.pagination),
                ("query", self.paginator.query),
                ("types", self.type_list),
                ("results", self.object_list),
                ("facets", self.facet_list),
            ]
        )

    @property
    def type_list(self) -> dict:
        # Takes a list of facets ['foo', 1, 'bar', 2] and converts them to
        # {'foo': 1, 'bar': 2} using some stupid python iterator tricks.
        facet_fields: dict = self.result.facets.get("facet_fields", {})
        facets: dict = facet_fields.get("type", {})

        type_numbers = {
            key: val
            for k in facets
            for key, val in k.items()
            if key in settings.SOLR["SEARCH_TYPES"]
        }

        image_count = self.result.facets["facet_fields"].get("source_with_images_b")
        image_numbers = {key: val for k in image_count for key, val in k.items()}
        type_numbers["sources_with_images"] = image_numbers.get("true", 0)

        return type_numbers

    @property
    def facet_list(self) -> dict:
        solr_facets = self.result.facets.get("facet_fields", None)
        pivot_facets = self.result.facets.get("facet_pivot", None)
        # facets: dict = {
        #     key: value
        #     for (key, value) in solr_facets.items()
        #     if key in settings.INTERFACE_FACETS
        # }
        # facets.update(pivot_facets)
        facets = {}
        for f, f_values in solr_facets.items():
            if f not in settings.INTERFACE_FACETS:
                continue

            facets[f] = [
                {"value": v, "count": c} for n in f_values for v, c in n.items()
            ]

        return facets

    @property
    def object_list(self) -> list:
        docs: list = self.result.docs
        data: list = SolrResultSerializer(
            docs, many=True, context={"request": self.paginator.request}
        ).data

        return data

    @property
    def pagination(self) -> dict:
        return OrderedDict(
            [
                ("next", self.next_url),
                ("previous", self.previous_url),
                ("first", self.first_url),
                ("last", self.last_url),
                ("current_page", self.number),
                ("num_pages", self.paginator.num_pages),
                # ('pages', pages)
            ]
        )

    @property
    def next_url(self) -> str | None:
        if not self.has_next:
            return None
        url: str = self.paginator.absolute_uri
        page_number = self.next_page_number
        return replace_query_param(url, "page", page_number)

    @property
    def previous_url(self) -> str | None:
        if not self.has_previous:
            return None
        url: str = self.paginator.absolute_uri
        page_number = self.previous_page_number
        return replace_query_param(url, "page", page_number)

    @property
    def first_url(self) -> str:
        url: str = self.paginator.absolute_uri
        return replace_query_param(url, "page", 1)

    @property
    def last_url(self) -> str | None:
        url: str = self.paginator.absolute_uri
        return replace_query_param(url, "page", self.paginator.num_pages)

    @property
    def has_next(self) -> int:
        return self.number < self.paginator.num_pages

    @property
    def has_previous(self) -> int:
        return self.number > 1

    @property
    def has_other_pages(self) -> int:
        return self.paginator.num_pages > 1

    @property
    def start_index(self) -> int:
        return (self.number - 1) * self.paginator.page_size

    @property
    def end_index(self) -> int:
        return self.start_index + len(self.result.docs) - 1

    @property
    def next_page_number(self) -> int:
        return self.number + 1

    @property
    def previous_page_number(self) -> int:
        return self.number - 1
