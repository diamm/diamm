import re
import serpy
from django.template.loader import get_template


class BibliographySearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    authors_s = serpy.MethodField()
    authors_ii = serpy.MethodField()

    title_s = serpy.StrField(
        attr="title"
    )
    year_s = serpy.StrField(
        attr="year"
    )
    year_ans = serpy.StrField(
        attr="year"
    )
    type_s = serpy.StrField(
        attr="type.name"
    )
    abbreviation_s = serpy.StrField(
        attr="abbreviation"
    )
    prerendered_sni = serpy.MethodField()
    sort_ans = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_authors_s(self, obj):
        """
            Construct a sortable author list representation, with authors separated by $:
            Position|Last Name|PK$Position|Last Name|PK$...

            This should allow authors to sort first by position, then by last name, and use their
            PK for reverse URL lookups on the other end.
        """
        authors = obj.authors.values_list('position',
                                          'bibliography_author__last_name',
                                          'bibliography_author__pk').order_by('position',
                                                                              'bibliography_author__last_name')
        authors_s = "$".join(["{0}|{1}|{2}".format(n[0], n[1], n[2]) for n in authors])
        return authors_s

    def get_authors_ii(self, obj):
        if obj.authors.count() > 0:
            return list(obj.authors.values_list('bibliography_author__pk', flat=True))
        return None

    def get_sort_ans(self, obj):
        if obj.authors.count() > 0:
            return " ".join(list(obj.authors.values_list('bibliography_author__last_name', flat=True)))
        return None

    def get_prerendered_sni(self, obj):
        """
            Pre-renders the citation by passing it through the Jinja template
            engine. This is an optimization to help reduce the amount of time
            needed to render the citation on request.
        """
        template = get_template('website/bibliography/bibliography_entry.jinja2')
        citation = template.template.render(content=obj)
        # strip out any newlines from the templating process
        citation = re.sub('\n', '', citation)
        # strip out multiple spaces
        citation = re.sub('\s+', ' ', citation)
        citation = citation.strip()
        return citation
