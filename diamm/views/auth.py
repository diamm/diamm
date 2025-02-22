import requests
import ujson
from django.conf import settings
from django.contrib import messages
from django.core import signing
from django.core.mail import send_mail
from django.http.response import HttpResponse
from django.views.generic.edit import FormView
from rest_framework import status
from rest_framework.reverse import reverse

from diamm.forms.create_account_form import CreateAccountForm
from diamm.models.diamm_user import CustomUserModel

REGISTRATION_SALT = getattr(settings, "REGISTRATION_SALT", "registration")


class CreateAccount(FormView):
    form_class = CreateAccountForm
    template_name = "website/auth/register.jinja2"
    success_url = "/"

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """
        If a user is already logged in, prevent them from accessing this form.
        """
        if request.user.is_authenticated:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)

        if "g-recaptcha-response" not in self.request.POST:
            # Something funny is going on -- we've received a POST request without the Recaptcha
            # value. Bail with a client error.
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        user_ip_address = self.request.META.get("REMOTE_ADDR")

        recaptcha_response = self.request.POST.get("g-recaptcha-response")

        r = requests.post(
            settings.GOOGLE_RECAPTCHA_ADDRESS,
            data={
                "secret": settings.GOOGLE_RECAPTCHA_SECRET,
                "response": recaptcha_response,
                "remoteip": user_ip_address,
            },
            timeout=10,
        )

        if not r or not r.text:
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        google_response = ujson.loads(r.text)

        if google_response["success"] is not True:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        # Ok, by this point we have:
        #  1. passed form validation, including password strength verification
        #  2. passed the CSRF validation on form submission
        #  3. passed the recaptcha test to check that it's not a bot.
        # So we should be able to create a new user account. We will set 'is_active' to false, and then send out an
        # e-mail confirmation which will change the status to 'true'.

        email = form.cleaned_data.get("email")
        affiliation = form.cleaned_data.get("affiliation")
        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        password = form.cleaned_data.get("password")

        d = {
            "affiliation": affiliation,
            "first_name": first_name,
            "last_name": last_name,
            "is_active": False,
        }

        u = CustomUserModel.objects.create_user(email=email, password=password, **d)

        activation_key = signing.dumps(
            obj=getattr(u, u.USERNAME_FIELD), salt=REGISTRATION_SALT
        )

        to_address = settings.ADMIN_EMAIL if settings.DEBUG else email
        confirmation_link = reverse(
            "registration_activate",
            request=self.request,
        )
        send_mail(
            "Registration Confirmation for DIAMM",
            settings.MAIL["CONFIRMATION_MESSAGE"].format(
                first_name=first_name,
                last_name=last_name,
                hostname=f"https://{settings.HOSTNAME}",
                confirmation_link=f"{confirmation_link}?activation_key={activation_key}",
            ),
            settings.DEFAULT_FROM_EMAIL,
            [to_address],
            fail_silently=False,
        )

        messages.success(
            self.request, "Thank you. You should receive a confirmation e-mail shortly."
        )

        return response
