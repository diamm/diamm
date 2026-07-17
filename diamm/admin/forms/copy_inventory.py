from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from diamm.models.data.source import Source


class CopyInventoryForm(forms.Form):
    class Media:
        css = {
            "all": (
                "admin/css/base.css",
                "admin/css/forms.css",
                "admin/css/widgets.css",
            )
        }
        js = [
            "admin/js/core.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
        ]

    def __init__(self, *args, **kwargs):
        self.source_instance = kwargs.pop("instance")
        super().__init__(*args, **kwargs)

    targets = forms.ModelMultipleChoiceField(
        queryset=Source.objects.all(),
        widget=FilteredSelectMultiple(verbose_name="Targets", is_stacked=False),
    )
