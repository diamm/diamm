import re

import serpy
from django.template.loader import get_template
from rest_framework.reverse import reverse

from diamm.serializers.serializers import ContextDictSerializer, ContextSerializer


class BibliographySerializer(ContextDictSerializer):
    entry = serpy.MethodField()
    pk = serpy.IntField()

    def get_entry(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj["citation_json"])
        # strip out any newlines from the templating process
        citation = re.sub(r"\n", "", citation)
        # strip out multiple spaces
        citation = re.sub(r"\s+", " ", citation)
        citation = citation.strip()
        return citation


class BibliographyAuthorSerializer(ContextSerializer):
    url = serpy.MethodField()
    last_name = serpy.StrField()
    first_name = serpy.StrField()
    bibliography = serpy.MethodField()

    def get_url(self, obj):
        return reverse(
            "author-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_bibliography(self, obj):
        return BibliographySerializer(
            obj.solr_bibliography,
            many=True,
            context={"request": self.context["request"]},
        ).data
