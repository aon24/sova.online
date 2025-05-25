'''
Created on 2025

@author: aon24
'''
from allauth.account.views import SignupView, LoginView
from allauth.account.forms import SignupForm
from django.forms.fields import CharField

from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from arm.settings import LOGIN_INVALID_URL
from arm.tools.DC import well
from arm.tools.common import cleanPhone

from django import forms


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



class CustomLoginView(LoginView):

    def form_invalid(self, form):
        return redirect(LOGIN_INVALID_URL)
