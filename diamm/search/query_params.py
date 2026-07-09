from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

from django.http import HttpRequest

FilterValue: TypeAlias = str | bool | list[str] | None


@dataclass(frozen=True)
class SearchQueryParams:
    query: str
    type_query: str | None
    filters: dict[str, FilterValue] = field(default_factory=dict)
    exclusive_filters: dict[str, FilterValue] = field(default_factory=dict)
    page: int = 1

    @classmethod
    def from_request(cls, request: HttpRequest) -> SearchQueryParams:
        filters: dict[str, FilterValue] = {}
        exclusive_filters: dict[str, FilterValue] = {}

        if "country_s" in request.GET:
            filters["country_s"] = f'"{request.GET.get("country_s")}"'
        if "cities" in request.GET:
            filters["city_s"] = [f'"{value}"' for value in request.GET.getlist("cities")]
        if "composer" in request.GET:
            filters["composers_ss"] = [
                f'"{value}"' for value in request.GET.getlist("composer")
            ]
        if "genre" in request.GET:
            exclusive_filters["genres_ss"] = [
                f'"{value}"' for value in request.GET.getlist("genre")
            ]
        if "notation" in request.GET:
            exclusive_filters["notations_ss"] = [
                f'"{value}"' for value in request.GET.getlist("notation")
            ]
        if "sourcetype" in request.GET:
            exclusive_filters["source_type_s"] = [
                f'"{value}"' for value in request.GET.getlist("sourcetype")
            ]
        if "has_inventory" in request.GET:
            filters["inventory_provided_b"] = request.GET.get("has_inventory")
        if "date_range" in request.GET:
            bounds = request.GET.get("date_range", "").split("to")
            if len(bounds) == 2:
                filters["facet_date_range_ii"] = f"[{bounds[0]} TO {bounds[1]}]"
        if "project" in request.GET:
            exclusive_filters["projects_ss"] = request.GET.get("project")
        if "anonymous" in request.GET:
            filters["anonymous_b"] = request.GET.get("anonymous")
        if "orgtype" in request.GET:
            filters["organization_type_s"] = f'"{request.GET.get("orgtype")}"'
        if "source_composers" in request.GET:
            filters["source_composers_ss"] = [
                f'"{value}"' for value in request.GET.getlist("source_composers")
            ]
        if "current_state" in request.GET:
            filters["current_state_s"] = [
                f'"{value}"' for value in request.GET.getlist("current_state")
            ]
        if "original_format" in request.GET:
            filters["original_format_s"] = [
                f'"{value}"' for value in request.GET.getlist("original_format")
            ]
        if "current_host" in request.GET:
            filters["current_host_s"] = [
                f'"{value}"' for value in request.GET.getlist("current_host")
            ]
        if "host_contents" in request.GET:
            filters["host_main_contents_s"] = [
                f'"{value}"' for value in request.GET.getlist("host_contents")
            ]

        try:
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            page = 1

        return cls(
            query=request.GET.get("q") or "*:*",
            type_query=request.GET.get("type"),
            filters=filters,
            exclusive_filters=exclusive_filters,
            page=page,
        )
