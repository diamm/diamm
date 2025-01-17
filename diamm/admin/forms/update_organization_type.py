from django import forms

from diamm.models.data.organization_type import OrganizationType


class UpdateOrganizationTypeForm(forms.Form):
    org_type = forms.ModelChoiceField(queryset=OrganizationType.objects.all())
