from django import forms
from django.utils.safestring import mark_safe
from diamm.models.diamm_user import CustomUserModel


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label="E-mail address",
        widget=forms.EmailInput(
            attrs={"class": "u-full-width"}
        )
    )

    def clean(self):
        email = self.cleaned_data.get('email')
        user_exists = CustomUserModel.objects.filter(email=email).exists()

        if not user_exists:
            err_msg = """
            No user with that e-mail address exists. <a href='/register/'>Create a new account</a>.
            """
            raise forms.ValidationError(mark_safe(err_msg))

