'''
Created on 2025

@author: aon24
'''
from arm.settings import LOGIN_INVALID_URL
from arm.tools.DC import well
from arm.tools.common import cleanPhone
from arm.api.doGet import _login
<<<<<<< HEAD
from arm.tools.first import err, snd
from arm.api.doGet import apiDoGet, _apiGetList
=======
from arm.tools.first import err
from arm.api.doGet import apiDoGet
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770
from arm.api.doPost import doPost
from arm.tools.dbToolkit.upload import uploadFile
from arm.tools.dbToolkit.download import downloadFile
import arm.tools.DC as dcm
<<<<<<< HEAD
=======
from arm.tools.httpMisc import notFound
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770

from allauth.account.views import SignupView, LoginView
from allauth.account.forms import SignupForm

from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django import forms
<<<<<<< HEAD
from django.http import HttpResponse, FileResponse, HttpResponseNotAllowed
=======
from django.http import HttpResponse, FileResponse
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770
from django.conf import settings

from urllib.parse import unquote
import os
from mimetypes import guess_type

# *** *** ***

def rsApi(request):
    if request.method == 'GET':
        if request.path.startswith('/api/download'):
            return downloadFile(request)
        else:
            return apiDoGet(request)
    elif request.method == 'POST':
        if request.path.startswith('/api/upload'):
            return uploadFile(request)
        else:
            return doPost(request)

<<<<<<< HEAD
    elif request.method == 'HEAD':
        if request.dcUK._path in _apiGetList:
            response = HttpResponse()
            # response.headers['Last-Modified'] = 'Mon, 02 Jun 2025 10:00:00 GMT'
            return response
        else:
            return custom_404_view(request, None)

    return HttpResponseNotAllowed(["GET", "HEAD"])
=======
    return custom_404_view(request)
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770

# *** *** ***

def custom_404_view(request, exception):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

<<<<<<< HEAD
    err(f"{request.user.username} ({ip}) {request.method}:{request.path}?{unquote(request.META['QUERY_STRING'])}", cat='Я 404')
=======
    err(f"{request.user.username} ({ip}) {request.path}?{unquote(request.META['QUERY_STRING'])}", cat='Я 404')
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770
    return HttpResponse(' ', status=404)

# *** *** ***

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

# *** *** ***

class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def get(self, request, *args, **kwargs):
        return _login(request)

# *** *** ***

class CustomLoginView(LoginView):

    def form_invalid(self, form):
        return redirect(LOGIN_INVALID_URL)

    def get(self, request, *args, **kwargs):
        return _login(request)

# *** *** ***


def homePage(request):
    redir = '/api/new' if request.user.is_authenticated else dcm.config.HOME_PAGE or '/login'
    return redirect(redir)

# ***


<<<<<<< HEAD
def home(request, f=None, **kwargs):
    return staticFiles(request, '/home' + request.path)
=======
def home(request):
    return staticFiles(request, '/home' + request.META['PATH_INFO'])
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770

# ***


<<<<<<< HEAD
def manifest(request):
    return HttpResponse(well('manifest.json'), 'application/json')


def staticFiles(request, fileName=None):
    try:
        fileName = fileName or request.path
=======
def staticFiles(request, fileName=None):
    try:
        fileName = fileName or request.META['PATH_INFO']
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770
        fileName = fileName.replace('/static', '')
        filePath = os.path.join(settings.STATIC_DIR, fileName[1:])
        filePath = os.path.normpath(filePath)  # Удаляет ../ и ./
        if os.path.exists(filePath):
<<<<<<< HEAD
            if request.method == 'HEAD':
                return HttpResponse()
            if request.method != 'GET':
                return HttpResponseNotAllowed(["GET", "HEAD"])

            with open(filePath, 'rb') as f:
                ip = request.META.get('HTTP_X_FORWARDED_FOR')
                ip = ip.split(',')[0] if ip else request.META.get('REMOTE_ADDR')
                snd(f"{request.user.username} ({ip}) {fileName}", cat='home')
                return HttpResponse(f.read(), guess_type(filePath)[0], headers=[('X-Frame-Options', 'SAMEORIGIN'), ])
                # return HttpResponse(f.read(), guess_type(filePath)[0], headers=[('X-Frame-Options', 'SAMEORIGIN'), ('Cache-Control', f'max-age={60 * 60 * 24 * 30}')])
    except:
        pass

    return custom_404_view(request, None)
=======
            with open(filePath, 'rb') as f:
                return HttpResponse(f.read(), guess_type(filePath)[0], headers=[('X-Frame-Options', 'SAMEORIGIN'), ])
    except Exception as ex:
        err(f'"{filePath}"\{ex}', cat='Static page')

    return notFound(request)
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770

# ***


def download_file(request):
<<<<<<< HEAD
    filePath = os.path.join(settings.STATIC_DIR, request.path[1:])
    filePath = os.path.normpath(filePath)
    if os.path.exists(filePath):
        if request.method == 'HEAD':
            return HttpResponse()
        if request.method != 'GET':
            return HttpResponseNotAllowed(["GET", "HEAD"])
        return FileResponse(open(filePath, 'rb'), as_attachment=True)

    return custom_404_view(request, None)
=======
    filePath = os.path.join(settings.STATIC_DIR, request.META['PATH_INFO'][1:])
    filePath = os.path.normpath(filePath)
    if os.path.exists(filePath):
        return FileResponse(open(filePath, 'rb'), as_attachment=True)

    return HttpResponse(f'"{filePath}" not found', status=404)
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770

# ***
