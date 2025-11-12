import math
from collections import OrderedDict

import pysolr
import ujson
import ypres
from django.conf import settings
from rest_framework.reverse import reverse
from rest_framework.utils.urls import replace_query_param

from diamm.helpers.formatters import format_person_name, contents_statement
from diamm.helpers.solr_helpers import SolrConnection


class SolrResultObject:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class SolrResultSerializer(ypres.DictSerializer):
    pk = ypres.StrField(attr="pk")
    url = ypres.MethodField()
    heading = ypres.MethodField()
    res_type = ypres.StrField(attr="type", label="type")
    display_name = ypres.StrField(attr="display_name_s", required=False)
    shelfmark = ypres.StrField(attr="shelfmark_s", required=False)
    archive_name = ypres.StrField(attr="archive_s", required=False)
    source_archive_city = ypres.MethodField()
    surface = ypres.StrField(attr="surface_type_s", required=False)
    source_type = ypres.StrField(attr="source_type_s", required=False)
    date_statement = ypres.MethodField()
    measurements = ypres.StrField(attr="measurements_s", required=False)
    inventory_provided = ypres.BoolField(attr="inventory_provided_b", required=False)
    number_of_compositions = ypres.IntField(
        attr="number_of_compositions_i", required=False
    )
    number_of_composers = ypres.IntField(attr="number_of_composers_i", required=False)
    notations = ypres.Field(attr="notations_ss", required=False)
    start_date = ypres.IntField(attr="start_date_i", required=False)
    end_date = ypres.IntField(attr="end_date_i", required=False)
    public_images = ypres.BoolField(attr="public_images_b", required=False)
    name = ypres.StrField(attr="name_s", required=False)
    location = ypres.StrField(attr="location_s", required=False)
    title = ypres.StrField(attr="title_s", required=False)
    composers = ypres.MethodField()
    siglum = ypres.StrField(attr="siglum_s", required=False)
    city = ypres.StrField(attr="city_s", required=False)
    country = ypres.StrField(attr="country_s", required=False)
    cluster_shelfmark = ypres.StrField(attr="cluster_shelfmark_s", required=False)
    archives = ypres.Field(attr="archives_ss", required=False)
    sources = ypres.MethodField()
    contents_statement = ypres.MethodField()

    def get_url(self, obj: dict) -> str:
        return reverse(
            f"{obj.get('type')}-detail",
            kwargs={"pk": obj.get("pk")},
            request=self.context.get("request"),
        )

    def get_heading(self, obj: dict) -> str:
        if "display_name_s" in obj:
            return obj["display_name_s"]
        elif "name_s" in obj:
            return obj["name_s"]
        elif "title_s" in obj:
            return obj["title_s"]
        elif "cluster_shelfmark_s" in obj:
            return obj["cluster_shelfmark_s"]
        else:
            return "[Unknown Heading]"

    def get_date_statement(self, obj) -> str | None:
        if {"date_statement_s", "start_date_i", "end_date_i"}.isdisjoint(obj.keys()):
            return None

        dstmt: str | None = obj.get("date_statement_s")
        strt: int | None = obj.get("start_date_i")
        end: int | None = obj.get("end_date_i")
        out = []
        range: str | None
        if strt and end:
            range = f"{strt}–{end}"
        elif strt and not end:
            range = f"{strt}-"
        elif not strt and end:
            range = f"—{end}"
        else:
            range = None

        if dstmt:
            out.append(f"{dstmt}")
            if range:
                out.append(f" ({range})")
            return "".join(out)
        elif range:
            return range
        else:
            return None

    def get_sources(self, obj: dict) -> int | None:
        if "sources_ii" in obj:
            return len(obj["sources_ii"])
        return None

    def get_composers(self, obj: dict) -> list[str] | None:
        ret: list[str] = []
        if obj.get("anonymous_b", False):
            ret.append("Anonymous")

        if "composers_json" not in obj:
            return ret

        composers: list = obj["composers_json"]
        ss = [format_person_name(composer) for composer in composers]

        return ret + ss

    def get_source_archive_city(self, obj) -> str | None:
        if "source_archive_city_s" not in obj:
            return None
        city_name = obj["source_archive_city_s"]

        if "source_archive_country_s" in obj:
            return f"{city_name}, {obj['source_archive_country_s']}"
        return city_name

    def get_contents_statement(self, obj) -> str | None:
        if obj["type"] != "source":
            return None

        return contents_statement(obj)


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
            "json.facet": ujson.dumps(settings.SOLR["JSON_FACETS"]),
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
        swi_numbers = image_numbers.get("true", 0)
        if swi_numbers > 0:
            type_numbers["sources_with_images"] = swi_numbers

        return type_numbers

    @property
    def facet_list(self) -> dict:
        solr_facets = self.result.facets.get("facet_fields", None)
        facets = {}
        for f, f_values in solr_facets.items():
            if f not in settings.INTERFACE_FACETS:
                continue

            if not f_values:
                continue

            out_facets = [
                {"value": v, "count": c} for n in f_values for v, c in n.items()
            ]

            facets[f] = sorted(out_facets, key=lambda d: d["value"].casefold())

        json_facets: dict | None = self.result.raw_response.get("facets")
        if (
            "full_date_range" in json_facets
            and "date_range" in json_facets
            and json_facets["date_range"].get("buckets")
        ):
            facets["date_range"] = {
                "min": json_facets["full_date_range"]["min_year"],
                "max": json_facets["full_date_range"]["max_year"],
                "buckets": [
                    {"value": v, "count": c}
                    for n in json_facets["date_range"]["buckets"]
                    for v, c in n.items()
                ],
            }

        return facets

    @property
    def object_list(self) -> list:
        docs: list = self.result.docs
        return SolrResultSerializer(
            docs, many=True, context={"request": self.paginator.request}
        ).serialized_many

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
