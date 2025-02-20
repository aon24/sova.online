from arm.api.doGet import apiDoGet
from arm.api.doPost import doPost
from arm.api.views import SignUpView
from arm.tools.dbToolkit.upload import uploadFile
from arm.tools.dbToolkit.download import downloadFile
from arm.tools.first import snd, err
from arm.tools.amgr import amgrLoop
from arm.tools.loadWell import loadWell
import arm.tools.DC as dcm
import arm.settings as armSetting

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.http import HttpResponse

import os
from mimetypes import guess_type
import threading

# Единственное место в Джанго, где можно настроить приложение

snd('=== Server started ===', cat='logging')
dcm.config = dcm.DC(armSetting.fromIni)
loadWell('all')
threading.Thread(target=amgrLoop).start()
snd('Amgr starts as new Thread.', cat='amgr')


def homePage(request):
    if request.user.is_authenticated:
        return redirect('/api/new')

    if dcm.config.HOME_PAGE:
        return redirect(dcm.config.HOME_PAGE)

    return getFiles('/static/home/home.html')


def staticFiles(request):
    return getFiles(request.META.get("PATH_INFO", ''))


def getImage(request):
    path = request.META.get("PATH_INFO", '').replace('/image', '/static/images')
    return getFiles(path)


def getVideo(request):
    path = request.META.get("PATH_INFO", '').replace('/video', '/static/media')
    return getFiles(path)

# ***

def getFiles(path):
    fn = 'file'
    try:
        if 'favicon.ico' in path:
            path = '/static/favicon.ico'
        else:
            if '..' in path:
                return HttpResponse(f'not found', status=404)

        fn = os.path.join(settings.BASE_DIR, path[1:])
        with open(fn, 'rb') as f:
            return HttpResponse(f.read(), guess_type(fn)[0])
    except:
        err(f'"{fn}" not found', cat='Static page')
        return HttpResponse(f'"{fn}" not found', status=404)

# ***
from allauth.account.views import SignupView

urlpatterns = [
    # path('/accounts/vk/login/callback/', apiDoGet),

    # api
    re_path('^api/post/', doPost),
    re_path('^api/upload', uploadFile),
    re_path('^api/download', downloadFile),
    re_path('^api/signup', SignUpView.as_view(), name="account_signup"),

    re_path('^api/', apiDoGet),

    re_path('^image/', getImage),
    re_path('^video/', getVideo),
    re_path('static/', staticFiles),

    re_path('^accounts/google/', apiDoGet),
    re_path('^accounts/vk/', apiDoGet),
    re_path('^accounts/yandex/', apiDoGet),

    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # new
    path('admin/logout', LogoutView.as_view(), name="logout"),

    re_path('favicon.ico', staticFiles),

    path('', homePage),
    path('login', apiDoGet),
    path('login/', apiDoGet),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

