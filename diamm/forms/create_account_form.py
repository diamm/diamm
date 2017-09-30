from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.safestring import mark_safe
from diamm.models.diamm_user import CustomUserModel


class CreateAccountForm(forms.Form):
    first_name = forms.CharField(
        required=True,
    )
    last_name = forms.CharField(
        required=True,
    )
    affiliation = forms.CharField(
        required=False,
    )
    email = forms.EmailField(
        required=True,
    )
    password = forms.CharField(
        required=True,
    )
    confirm_password = forms.CharField(
        required=True,
    )

    def clean(self):
        """
            Validates that
             - the user agreement has been checked (see the form template for the checkbox form field; the text for this
             was lengthy and did not fit in the space provided for form help text)
             - an existing user with the e-mail address does not exist
             - the passwords are present
             - that they match
             - that the passwords meet minimum security standards.

        :return: None; will raise validation error if a condition is not met.
        """
        cleaned_data = super(CreateAccountForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')

        if 'user-agreement' not in self.data:
            agreement_err = """
                You must agree to the user terms and conditions.
            """
            err = forms.ValidationError(agreement_err)
            raise err

        email_exists = CustomUserModel.objects.filter(email=email).exists()

        if email_exists:
            email_err = """
                A user with the e-mail address {0} already exists. Try <a href='/reset'>recovering your password</a>.
            """
            err = forms.ValidationError(mark_safe(email_err.format(email)))
            raise err

        if not password:
            err = forms.ValidationError('You must supply a password')
            self.add_error('password', err)
            raise err

        if not confirm_password:
            err = forms.ValidationError('You must re-type your password to confirm')
            self.add_error('confirm_password', err)
            raise err

        if password != confirm_password:
            err = forms.ValidationError('Your passwords did not match')
            self.add_error('password', err)
            self.add_error('confirm_password', err)
            raise err

        try:
            validate_password(password)
        except forms.ValidationError as err:
            self.add_error('password', err)
            raise err
