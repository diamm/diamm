from django import forms

from diamm.admin.helpers.source_picker import (
    SourceRelationshipAutocompleteSelect,
    source_relationship_picker_label,
)
from diamm.models import Page, Source, SourceToSourceRelationship


class ExportPagesForm(forms.Form):
    target = forms.ModelChoiceField(
        queryset=Source.objects.none(), label="Target source"
    )
    pages = forms.ModelMultipleChoiceField(
        queryset=Page.objects.none(),
        widget=forms.SelectMultiple(attrs={"size": 16}),
        help_text="Select one or more pages to copy to the target source.",
    )

    def __init__(self, *args, source, admin_site, **kwargs):
        super().__init__(*args, **kwargs)
        target = self.fields["target"]
        target.queryset = Source.objects.exclude(pk=source.pk).select_related(
            "archive"
        )
        target.label_from_instance = source_relationship_picker_label
        target.widget = SourceRelationshipAutocompleteSelect(
            SourceToSourceRelationship._meta.get_field("to_source"),
            admin_site,
        )
        target.widget.is_required = target.required
        target.widget.choices = target.choices

        pages = self.fields["pages"]
        pages.queryset = source.pages.order_by("sort_order", "pk")
        pages.label_from_instance = self.page_label

    @staticmethod
    def page_label(page):
        page_kind = f" — {page.page_kind}" if page.page_kind else ""
        return f"{page.numeration}{page_kind} (ID {page.pk})"
