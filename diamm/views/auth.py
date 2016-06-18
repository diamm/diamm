import json
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, password_validation
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.core.validators import validate_email
from django import forms
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import views
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from diamm.renderers.html_renderer import HTMLRenderer


class SessionAuth(views.APIView):
    """
        A note on status codes:
        401: Users are not authenticated, but they may be given a chance to authorize.
        403: Users are authenticated (we know who they are) but for some reason they are forbidden. They
        don't get another chance.
    """
    template_name = "website/auth/login.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def post(self, request, *args, **kwargs):
        if request.is_ajax:
            username = request.data.get('username', None)
            password = request.data.get('password', None)

            if not username:
                return Response({'detail': "You must supply a username"}, status=status.HTTP_401_UNAUTHORIZED)

            u = User.objects.filter(username=username)

            #check if user is in database
            if u.count() > 0:
                if u[0].last_login is None:
                    send_mail(
                        'DIAMM Account Password Change',
                        'Here is the message.',
                        'arielle.goldman@mail.mcgill.ca',
                        ['arielle745@hotmail.com'],
                        fail_silently=False,
                    )
                    return Response({'old_user': True})
            #if current user, send response to display the password field
                if not password:
                    return Response({'old_user': False, 'password': False})

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    #if isinstance(request.accepted_renderer, HTMLRenderer):
                    return Response({'password': True, 'old_user': False, 'redirect': reverse('user-profile', kwargs={'pk': user.pk})})
                else:
                    # user exists but is not active; forbid them access.
                    return Response({}, status=status.HTTP_403_FORBIDDEN)

            # user does not exist. Assume a typo and allow them to re-authenticate
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({})


class AccountUpdate(views.APIView):
    template_name = "website/auth/update.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def post(self, request, *args, **kwargs):
        username = request.DATA.get('username', None)
        email = request.DATA.get('email', None)

        # Check inputs
        # Send email
        # Return Response
        return HttpResponseRedirect("/login/email-sent")

    def get(self, request, *args, **kwargs):
        return Response({})


class AccountEmailSent(views.APIView):
    template_name = "website/auth/email_sent.html"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        return Response({})


class CreateAccount(views.APIView):
    template_name = "website/auth/login.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        conf_password = request.data.get('conf_password', None)
        email = request.data.get('email', None)
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        try:
            validate_email(email)
        except forms.ValidationError:
            return Response("Invalid email", status=status.HTTP_401_UNAUTHORIZED)
        try:
            password_validation.validate_password(password)
        except forms.ValidationError:
            return Response("Invalid password", status=status.HTTP_401_UNAUTHORIZED)

        if username and password and email:

            if password != conf_password:
                return Response("Passwords do not match", status=status.HTTP_401_UNAUTHORIZED)

            if User.objects.filter(email=email):
                return Response("Email is taken", status=status.HTTP_401_UNAUTHORIZED)

            user = User.objects.create_user(username,
                                            email,
                                            password)
            user.first_name = first_name
            user.last_name = last_name
            user.last_login = datetime.now()
            user.save()
            u = authenticate(username=username, password=password)
            if u:
                login(request, u)
                print("done")
                return Response({'redirect': reverse('user-profile', kwargs={'pk': user.pk})})
        else:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        return Response({})


class AccountInfo(views.APIView):
    template_name = "website/auth/account_info.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        return Response({})


class SessionClose(views.APIView):
    """
        POST to log out. This will clear the session ID.
    """
    template_name = "website/auth/logout.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def post(self, request, *args, **kwargs):

        if request.user.is_authenticated():
            logout(request)

            if isinstance(request.accepted_renderer, HTMLRenderer):
                return HttpResponseRedirect(reverse("home"))
            return Response({})
        else:
            # unauthenticated users are forbidden from the logout page.
            return Response({}, status=status.HTTP_403_FORBIDDEN)
