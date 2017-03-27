from django import forms


class MergeOrganizationsForm(forms.Form):
    keep_old = forms.BooleanField(initial=True, required=False)
