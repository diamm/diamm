import re
import serpy
from django.template.loader import get_template


class ItemBibliographySearchSerializer(serpy.Serializer):
    pk = serpy.IntField()
    type = serpy.MethodField()
    item_i = serpy.IntField(
        attr="item.pk"
    )
    pages_s = serpy.StrField(
        attr="pages",
        required=False
    )
    notes_s = serpy.StrField(
        attr="notes",
        required=False
    )
    prerendered_s = serpy.MethodField()

    def get_prerendered_s(self, obj):
        """
            Pre-renders the citation by passing it through the Jinja template
            engine. This is an optimization to help reduce the amount of time
            needed to render the citation on request.
        """
        template = get_template('website/bibliography/bibliography_entry.jinja2')
        citation = template.template.render(content=obj.bibliography)
        citation = re.sub('\n', '', citation)
        citation = re.sub('\s+', ' ', citation)
        citation = citation.strip()
        return citation

    def get_type(self, obj):
        return obj.__class__.__name__.lower()
