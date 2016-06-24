import datetime
import requests
import ujson
import uuid
from django.utils import timezone
from django.views.generic.edit import FormView
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse, HttpResponse
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.reverse import reverse
from diamm.forms.login_form import LoginForm
from diamm.forms.create_account_form import CreateAccountForm
from diamm.forms.reset_password_form import ResetPasswordForm
from diamm.models.diamm_user import CustomUserModel


class LoginView(FormView):
    form_class = LoginForm
    template_name = "website/auth/login.jinja2"
    success_url = "/"

    def form_invalid(self, form):
        """
            If the form is invalid and the mode of access is an API request,
            returns a 401 unauthorized (allowing the client to re-try their connection).

            Otherwise returns form validation errors, allowing the client to fix their mistakes and re-try.
        """
        response = super(LoginView, self).form_invalid(form)
        if self.request.META.get("HTTP_ACCEPT") == "application/json":
            return JsonResponse({"success": False, "errors": form.errors}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return response

    def form_valid(self, form):
        """
            If the login form is valid (username/password present), logs the user in.
        """
        response = super(LoginView, self).form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            if self.request.META.get("HTTP_ACCEPT") == "application/json":
                return JsonResponse({'success': True})
            else:
                return response
        else:
            if self.request.META.get("HTTP_ACCEPT") == "application/json":
                return JsonResponse({'success': False}, status=status.HTTP_403_FORBIDDEN)
            else:
                return response


class LogoutView(View):
    """
        Handles logout calls. Returns a 403 forbidden if a user is not authenticated
    """
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            logout(request)
            if self.request.META.get("HTTP_ACCEPT") == "application/json":
                return JsonResponse({"success": True})
            else:
                return HttpResponseRedirect(reverse('home'))
        else:
            if self.request.META.get("HTTP_ACCEPT") == "application/json":
                return JsonResponse({"success": False}, status=status.HTTP_403_FORBIDDEN)
            else:
                return HttpResponse(status=status.HTTP_403_FORBIDDEN)


class CreateAccount(FormView):
    form_class = CreateAccountForm
    template_name = "website/auth/register.jinja2"
    success_url = "/"

    def form_valid(self, form):
        response = super(CreateAccount, self).form_valid(form)

        if not 'g-recaptcha-response' in self.request.POST:
            # Something funny is going on -- we've received a POST request without the Recaptcha
            # value. Bail with a client error.
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        user_ip_address = self.request.META.get("REMOTE_ADDR")

        recaptcha_response = self.request.POST.get('g-recaptcha-response')

        r = requests.post(settings.GOOGLE_RECAPTCHA_ADDRESS, data={
            'secret': settings.GOOGLE_RECAPTCHA_SECRET,
            'response': recaptcha_response,
            'remoteip': user_ip_address
        })

        if not r or not r.text:
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        google_response = ujson.loads(r.text)

        if google_response['success'] is not True:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        # Ok, by this point we have:
        #  1. passed form validation, including password strength verification
        #  2. passed the CSRF validation on form submission
        #  3. passed the recaptcha test to check that it's not a bot.
        # So we should be able to create a new user account. We will set 'is_active' to false, and then send out an
        # e-mail confirmation which will change the status to 'true'.

        email = form.cleaned_data.get('email')
        affiliation = form.cleaned_data.get('affiliation')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        password = form.cleaned_data.get('password')
        activation_key = str(uuid.uuid4())

        d = {
            'affiliation': affiliation,
            'first_name': first_name,
            'last_name': last_name,
            'is_active': False,
            'temp_activation_key': activation_key
        }

        u = CustomUserModel.objects.create_user(
            email=email,
            password=password,
            **d
        )

        if settings.DEBUG:
            to_address = "andrew.hankinson@gmail.com"
        else:
            to_address = email

        send_mail(
            "Registration Confirmation for DIAMM",
            settings.MAIL['CONFIRMATION_MESSAGE'].format(
                first_name=first_name,
                last_name=last_name,
                hostname="https://{0}".format(settings.HOSTNAME),
                confirmation_link=reverse('activate',
                                          kwargs={"uuid": activation_key},
                                          request=self.request)
            ),
            settings.MAIL['FROM'],
            [to_address],
            fail_silently=False
        )

        return response


class ResetPassword(FormView):
    form_class = ResetPasswordForm
    template_name = "website/auth/reset.jinja2"
    success_url = "/"


class ActivateAccount(View):
    template_name = "website/auth/confirmation.jinja2"

    def get(self, request, uuid, *args, **kwargs):
        success = False

        # Look up the user by the UUID they supplied
        u = CustomUserModel.objects.filter(temp_activation_key=uuid)

        if not u.exists():
            return render(self.request, self.template_name, {"content": "A user with that confirmation token was not found.", "success": False})

        # get the first / only result (there should only ever be one)
        u = u.first()

        # If the user exists, check their join date. If the activation is greater than a day old, reject it.
        difference = timezone.now() - u.date_joined
        if difference.days > 1:
            u.temp_activation_key = None
            u.save()
            # TODO: Link for re-sending the confirmation e-mail.
            message = "This confirmation link has expired."
            success = False
        else:
            u.temp_activation_key = None
            u.is_active = True
            u.save()
            message = "Confirmation success. You may now log in."
            success = True

        return render(self.request, self.template_name, {'content': message, 'success': success})
