from django import forms
from django.utils.safestring import mark_safe
from diamm.models.diamm_user import CustomUserModel


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "u-full-width"}
        ),
    )

    new_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "u-full-width"}
        ),
    )

    new_password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "u-full-width"}
        ),
    )

