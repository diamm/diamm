from django import forms


class MergeAreasForm(forms.Form):
    keep_old = forms.BooleanField(initial=True, required=False)
