from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet


class MergeForm(forms.Form):
    target = forms.ModelChoiceField(
        queryset=None,
        help_text="All selected records will be merged into this record.",
    )
    keep_old = forms.BooleanField(
        initial=True,
        required=False,
        help_text="Keep the emptied alias records after moving their data.",
    )

    def __init__(self, *args, queryset: QuerySet, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.queryset = queryset
        self.fields["target"].queryset = queryset
        self.fields["target"].initial = queryset.first()

    def clean(self):
        cleaned_data = super().clean()
        if self.queryset.count() < 2:
            raise ValidationError("Select at least two records to merge.")
        return cleaned_data
