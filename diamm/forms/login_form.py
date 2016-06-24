from django import forms


class LoginForm(forms.Form):
    username = forms.EmailField(
        label="E-mail address",
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "u-full-width"}
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "u-full-width"}
        ),
    )
