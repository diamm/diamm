from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import generics, response, status

from diamm.helpers.solr_pagination import (
    PageRangeOutOfBoundsException,
    SolrPaginator,
    SolrResultException,
)


class SearchView(generics.GenericAPIView):
    template_name = "website/search/search.jinja2"

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs) -> response.Response:
        query = request.GET.get("q", None)
        filters = {}
        exclusive_filters = {}  # these will get ANDed... the others will get ORed
        sorts = ["score desc"]

        # On a blank query retrieve everything, but sort
        # by archive_city_s so that sources sort to the top.
        if not query:
            query = "*:*"

        filters.update({"{!tag=type}type": settings.SOLR["SEARCH_TYPES"]})
        if not request.user.is_staff:
            filters.update({"public_b": True})

        type_query = request.GET.get("type", None)

        # adjusts the sorting for each type
        if type_query and type_query in settings.SOLR["TYPE_SORTS"]:
            sorts.append(settings.SOLR["TYPE_SORTS"][type_query])
        else:
            sorts.append("display_name_s asc")

        # if we have an active query but want all types.
        if query and type_query == "all":
            filters.update({"{!tag=type}type": settings.SOLR["SEARCH_TYPES"]})
        elif type_query and type_query in settings.SOLR["SEARCH_TYPES"]:
            filters.update({"{!tag=type}type": type_query})
        elif type_query and type_query == "sources_with_images":
            # external manifest items should show up in sources with images.
            filters.update(
                {
                    "{!tag=type}type": "source",
                    "{!tag=type}source_with_images_b": True,
                }
            )

        if "country_s" in request.GET:
            filters.update({"country_s": f'"{request.GET.get("country_s")}"'})
        if "cities" in request.GET:
            filters.update(
                {"city_s": [f'"{g}"' for g in request.GET.getlist("cities")]}
            )

        if "composer" in request.GET:
            filters.update(
                {"composers_ss": [f'"{g}"' for g in request.GET.getlist("composer")]}
            )

        if "genre" in request.GET:
            exclusive_filters.update(
                {"genres_ss": [f'"{g}"' for g in request.GET.getlist("genre")]}
            )

        if "notation" in request.GET:
            exclusive_filters.update(
                {"notations_ss": [f'"{g}"' for g in request.GET.getlist("notation")]}
            )

        if "sourcetype" in request.GET:
            exclusive_filters.update(
                {"source_type_s": [f'"{g}"' for g in request.GET.getlist("sourcetype")]}
            )

        if "has_inventory" in request.GET:
            filters.update(
                {"inventory_provided_b": request.GET.get("has_inventory", None)}
            )

        if "date_range" in request.GET:
            res = request.GET.get("date_range", "").split("to")
            if len(res) == 2:
                filters.update({"facet_date_range_ii": f"[{res[0]} TO {res[1]}]"})

        # Filter search by Anonymous Compositions
        if "anonymous" in request.GET:
            filters.update({"anonymous_b": request.GET.get("anonymous", None)})
            # Overwrite the first sort
            sorts[0] = "title_ans asc"

        # Filter search by organization type
        if "orgtype" in request.GET:
            filters.update(
                {"organization_type_s": f'"{request.GET.get("orgtype", None)}"'}
            )

        if "source_composers" in request.GET:
            filters.update(
                {
                    "source_composers_ss": [
                        f'"{g}"' for g in request.GET.getlist("source_composers")
                    ]
                }
            )

        if "current_state" in request.GET:
            filters.update(
                {
                    "current_state_s": [
                        f'"{g}"' for g in request.GET.getlist("current_state")
                    ]
                }
            )

        if "original_format" in request.GET:
            filters.update(
                {
                    "original_format_s": [
                        f'"{g}"' for g in request.GET.getlist("original_format")
                    ]
                }
            )

        if "current_host" in request.GET:
            filters.update(
                {
                    "current_host_s": [
                        f'"{g}"' for g in request.GET.getlist("current_host")
                    ]
                }
            )

        if "host_contents" in request.GET:
            filters.update(
                {
                    "host_main_contents_s": [
                        f'"{g}"' for g in request.GET.getlist("host_contents")
                    ]
                }
            )

        try:
            page_num = int(request.GET.get("page", 1))
        except ValueError:
            page_num = 1

        sorts_str = ", ".join(sorts)

        try:
            paginator = SolrPaginator(
                query, filters, exclusive_filters, sorts_str, request
            )
        except SolrResultException as e:
            # We assume that an exception raised by Solr is the result of a bad request by the client,
            #  so we bubble up a 400 with a message about why it went wrong.
            return response.Response(
                {"message": repr(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            page = paginator.page(page_num)
        except PageRangeOutOfBoundsException:
            # If requesting past the number of pages, punt the user back to page 1.
            page = paginator.page(1)

        return response.Response(page.get_paginated_response())
