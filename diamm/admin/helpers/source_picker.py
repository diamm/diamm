from django.contrib.admin.widgets import AutocompleteSelect
from django.urls import reverse


def source_picker_label(source) -> str:
    date = source.date_statement or "undated"
    return f"{source.archive.siglum} {source.shelfmark} — {date}"


def source_relationship_picker_label(source) -> str:
    name = f" ({source.name})" if source.name else ""
    return f"{source.archive.siglum} {source.shelfmark}{name}"


class SourceRelationshipAutocompleteSelect(AutocompleteSelect):
    def get_url(self):
        return reverse("admin:source-relationship-autocomplete")
