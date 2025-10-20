import re

import ypres
from django.db.models.expressions import F, Value
from django.db.models.functions.text import Concat
from django.template.loader import get_template
from rest_framework.reverse import reverse

from diamm import settings
from diamm.helpers.solr_helpers import SolrManager


class SetBibliographySerializer(ypres.DictSerializer):
    pk = ypres.IntField()
    prerendered = ypres.MethodField()
    pages = ypres.StrField(required=False)
    notes = ypres.StrField(required=False)

    def get_prerendered(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj["citation_json"])
        # strip out any newlines from the templating process
        citation = re.sub(r"\n", "", citation)
        # strip out multiple spaces
        citation = re.sub(r"\s+", " ", citation)
        citation = citation.strip()
        return citation


class SetDetailSerializer(ypres.Serializer):
    pk = ypres.IntField()
    url = ypres.MethodField()
    type = ypres.StrField(attr="set_type")
    cluster_shelfmark = ypres.StrField()
    holding_archives = ypres.MethodField()
    sources = ypres.MethodField()
    description = ypres.StrField(required=False)
    bibliography = ypres.MethodField()

    def get_url(self, obj) -> str:
        return reverse(
            "set-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_bibliography(self, obj) -> list[dict]:
        connection = SolrManager(settings.SOLR["SERVER"])
        fq = ["type:bibliography", f"sets_ii:{obj.pk}"]
        connection.search("*:*", fq=fq, sort="year_ans desc, sort_ans asc")

        if connection.hits == 0:
            return []

        reslist = []
        for res in connection.results:
            if "sets_json" in res:
                entry_list = [
                    s for s in res["sets_json"] if s and s["set_id"] == obj.pk
                ]
                if not entry_list:
                    continue
                entry = entry_list[0]
                if p := entry.get("pages"):
                    res["pages"] = p
                if n := entry.get("notes"):
                    res["notes"] = n

                reslist.append(SetBibliographySerializer(res).serialized)

        return reslist

    def get_holding_archives(self, obj) -> list[dict]:
        archives = (
            obj.sources.annotate(
                archive_name=Concat(
                    F("archive__name"), Value(" ("), F("archive__siglum"), Value(")")
                )
            )
            .values_list("archive_name", "archive_id")
            .order_by("archive__name")
            .distinct("archive__name")
        )
        res = []
        for archive in archives:
            res.append(
                {
                    "url": reverse(
                        "archive-detail",
                        kwargs={"pk": archive[1]},
                        request=self.context["request"],
                    ),
                    "name": archive[0],
                }
            )

        return res

    def get_sources(self, obj) -> list:
        req = self.context["request"]
        is_staff = req.user.is_staff

        connection = SolrManager(settings.SOLR["SERVER"])
        fq: list = ["type:set", f"pk:{obj.pk}"]

        connection.search("*:*", fq=fq)

        if connection.hits == 0:
            return []

        result: dict | None = connection.first
        if result is None:
            return []

        sources = result.get("sources_json", [])
        ret = []

        for source in sources:
            if not source.get("public", False) and not is_staff:
                continue

            url = reverse(
                "source-detail",
                kwargs={
                    "pk": source["pk"],
                },
                request=self.context["request"],
            )
            if c := source.get("cover_image"):
                cover = reverse(
                    "cover-image",
                    kwargs={"pk": c},
                    request=self.context["request"],
                )
            else:
                cover = None

            ret.append(
                {
                    "display_name": source["display_name"],
                    "url": url,
                    "cover_image": cover,
                }
            )

        return ret

    # return SetSourceSerializer(
    #         obj.sources.all(),
    #         many=True,
    #         context={"request": self.context["request"]},
    #     ).data
