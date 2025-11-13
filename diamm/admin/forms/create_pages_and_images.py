from django import forms


class CreatePagesAndImagesForm(forms.Form):
    public = forms.BooleanField(
        initial=True, required=False, label="Make all images public"
    )
    imports = forms.CharField(widget=forms.Textarea(attrs={"rows": 80, "cols": 100}))
