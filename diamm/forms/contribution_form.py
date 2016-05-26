from django import forms
from diamm.models.site.contribution import Contribution


class ContributionForm(forms.ModelForm):

    class Meta:
        model = Contribution
        fields = ['note', 'object_id', 'content_type']
