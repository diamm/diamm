import re

import ypres
from django.template.loader import get_template
from rest_framework.reverse import reverse


class BibliographySerializer(ypres.DictSerializer):
    entry = ypres.MethodField()
    pk = ypres.IntField()

    def get_entry(self, obj):
        template = get_template("website/bibliography/bibliography_entry.jinja2")
        citation = template.template.render(content=obj["citation_json"])
        # strip out any newlines from the templating process
        citation = re.sub(r"\n", "", citation)
        # strip out multiple spaces
        citation = re.sub(r"\s+", " ", citation)
        citation = citation.strip()
        return citation


class BibliographyAuthorSerializer(ypres.Serializer):
    url = ypres.MethodField()
    last_name = ypres.StrField()
    first_name = ypres.StrField()
    bibliography = ypres.MethodField()

    def get_url(self, obj):
        return reverse(
            "author-detail", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_bibliography(self, obj):
        return BibliographySerializer(
            obj.solr_bibliography,
            many=True,
            context={"request": self.context["request"]},
        ).serialized_many
