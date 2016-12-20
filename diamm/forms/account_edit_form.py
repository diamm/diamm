from django import forms


class AccountEditForm(forms.Form):
    email = forms.EmailField(
        required=True,
        help_text="Note: Changing your e-mail address will change the username with which you log in."
    )

    first_name = forms.CharField(
        required=True,
    )
    last_name = forms.CharField(
        required=True,
    )
    affiliation = forms.CharField(
        required=True,
    )
