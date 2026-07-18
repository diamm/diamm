from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from django.urls import reverse

from diamm.admin.helpers.source_picker import source_picker_label
from diamm.models import (
    Page,
    Source,
    SourceToSourceRelationship,
    SourceToSourceRelationshipType,
)


class DonorSourceAutocompleteSelect(AutocompleteSelect):
    def get_url(self):
        return reverse("admin:virtual-source-donor-autocomplete")


class DonorSourceForm(forms.Form):
    donor = forms.ModelChoiceField(
        queryset=Source.objects.none(), label="Source to copy pages from"
    )

    def __init__(self, *args, target, admin_site, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields["donor"]
        field.queryset = (
            Source.objects.filter(is_virtual=False, pages__isnull=False)
            .exclude(pk=target.pk)
            .select_related("archive__city")
            .distinct()
        )
        field.label_from_instance = source_picker_label
        field.widget = DonorSourceAutocompleteSelect(
            SourceToSourceRelationship._meta.get_field("to_source"), admin_site
        )
        field.widget.is_required = field.required
        field.widget.choices = field.choices


class VirtualSourcePagesForm(forms.Form):
    pages = forms.ModelMultipleChoiceField(
        queryset=Page.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Only internal pages not already copied to this virtual source are shown.",
    )
    relationship_type = forms.ModelChoiceField(
        queryset=SourceToSourceRelationshipType.objects.all(),
        required=False,
        help_text="Optionally record a directed relationship from the virtual source to the donor.",
    )

    def __init__(self, *args, target, donor, **kwargs):
        super().__init__(*args, **kwargs)
        copied_ids = target.pages.exclude(copied_from=None).values_list(
            "copied_from_id", flat=True
        )
        self.fields["pages"].queryset = (
            donor.pages.filter(external=False)
            .exclude(pk__in=copied_ids)
            .order_by("sort_order", "pk")
        )

    @property
    def preview_counts(self):
        if not self.is_valid():
            return None
        pages = self.cleaned_data["pages"]
        existing_original_ids = pages.model.objects.filter(
            pk__in=pages.values("pk"), items__isnull=False
        ).values_list("items__pk", flat=True)
        return {
            "pages": pages.count(),
            "items": len(set(existing_original_ids)),
        }
