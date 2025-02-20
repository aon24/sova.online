'''
Created on 2025

@author: aon24
'''
from allauth.account.views import SignupView
from allauth.account.forms import SignupForm
from django.forms.fields import CharField


class SignupFields(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'] = CharField(required=False, max_length=150)
        self.fields['first_name'] = CharField(required=False, max_length=150)


class SignUpView(SignupView):
    form_class = SignupFields

