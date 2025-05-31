'''
Created on 2025

@author: aon24
'''
from arm.settings import LOGIN_INVALID_URL
from arm.tools.DC import well
from arm.tools.common import cleanPhone
from arm.api.doGet import _login
from arm.tools.first import err

from allauth.account.views import SignupView, LoginView
from allauth.account.forms import SignupForm

from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django import forms
from django.http import HttpResponse

from urllib.parse import unquote


def custom_404_view(request, exception):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    err(f"{request.user.username} ({ip}) {request.path}?{unquote(request.META['QUERY_STRING'])}", cat='Я 404')
    return HttpResponse(' ', status=404)


class CustomSignupForm(SignupForm):
    last_name = forms.CharField(required=True, max_length=150)
    first_name = forms.CharField(required=True, max_length=150)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('first_name'):
            raise ValidationError("Empty first name")

        phone = cleaned_data.get('last_name')
        phone = cleanPhone(phone)
        profile = well('profilesByPhone', phone)
        if not profile:
            raise ValidationError("Sorry, only for own")

        if profile.user_id:
            raise ValidationError("The user already exists")

        return cleaned_data


class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def get(self, request, *args, **kwargs):
        return _login(request)


class CustomLoginView(LoginView):

    def form_invalid(self, form):
        return redirect(LOGIN_INVALID_URL)

    def get(self, request, *args, **kwargs):
        return _login(request)

