from django import forms


class MergeCompositionsForm(forms.Form):
    keep_old = forms.BooleanField(initial=True, required=False)
