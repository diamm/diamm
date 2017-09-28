from django import forms
from diamm.models.data.genre import Genre


class AssignGenreForm(forms.Form):
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all()
    )
