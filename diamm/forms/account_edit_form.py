from django import forms


class AccountEditForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "u-full-width"}
        ),
        help_text="Note: Changing your e-mail address will change the username with which you log in."
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": "u-full-width"}
        )
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": "u-full-width"}
        )
    )
    affiliation = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": "u-full-width"}
        )
    )
