from django import forms


class RotationForm(forms.Form):
    rotation = forms.TypedChoiceField(
        choices=((90, "90° clockwise"), (180, "180°"), (270, "270° clockwise")),
        coerce=int,
        initial=180,
    )
