from django import forms


class MergePeopleForm(forms.Form):
    keep_old = forms.BooleanField(initial=True, required=False)
