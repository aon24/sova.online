from arm.api.doGet import apiDoGet
from arm.api.doPost import doPost
from arm.views import CustomSignupView, CustomLoginView
from arm.tools.dbToolkit.upload import uploadFile
from arm.tools.dbToolkit.download import downloadFile
from arm.tools.first import snd, err
from arm.tools.amgr import amgrLoop
from arm.tools.loadWell import loadWell, well
import arm.tools.DC as dcm
from arm.tools.httpMisc import notFound

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from django.shortcuts import redirect
from django.http import HttpResponse, FileResponse

import os
from mimetypes import guess_type
import threading

# Единственное место в Джанго, где можно настроить приложение

snd('=== Server started ===', cat='logging')
loadWell('all')
threading.Thread(target=amgrLoop).start()
snd('Amgr starts as new Thread.', cat='amgr')


def homePage(request):
    redir = '/api/new' if request.user.is_authenticated else dcm.config.HOME_PAGE or '/login'
    return redirect(redir)


def staticFiles(request):
    return getFiles(request, request.META['PATH_INFO'].replace('/static/', ''))


def getImage(request):
    pat = request.META['PATH_INFO'].replace('/image', 'images')
    return getFiles(request, pat)


def getVideo(request):
    pat = request.META['PATH_INFO'].replace('/video', 'media')
    return getFiles(request, pat)


# ***
def manifest(request):
    return HttpResponse(well('manifest.json'), 'application/json')


def getFiles(request, fileName):
    try:
        if 'favicon.ico' in fileName:
            fileName = 'favicon.ico'

        filePath = os.path.join(settings.STATIC_DIR, fileName)
        filePath = os.path.normpath(filePath)  # Удаляет ../ и ./
        if os.path.exists(filePath):
            with open(filePath, 'rb') as f:
                return HttpResponse(f.read(), guess_type(filePath)[0], headers=[('X-Frame-Options', 'SAMEORIGIN'), ])
    except Exception as ex:
        err(f'"{filePath}"\{ex}', cat='Static page')

    return notFound(request)

# ***


def download_file(request):
    filePath = os.path.join(settings.STATIC_DIR, request.META['PATH_INFO'][1:])
    filePath = os.path.normpath(filePath)
    if os.path.exists(filePath):
        return FileResponse(open(filePath, 'rb'), as_attachment=True)

    return HttpResponse(f'"{filePath}" not found', status=404)

# ***


handler404 = 'arm.views.custom_404_view'

urlpatterns = [
    # api
    re_path('^api/post/', doPost),
    re_path('^api/upload', uploadFile),
    re_path('^api/download', downloadFile),
    re_path('^api/signup', CustomSignupView.as_view(), name="account_signup"),

    re_path('^api/', apiDoGet),

    re_path('^image/', getImage),
    re_path('^video/', getVideo),
    re_path('^static/', staticFiles),  # in DEBUG-mode работает странно: подключает свои обработчики
    re_path('^download/', download_file),

    re_path('login/', CustomLoginView.as_view(), name="account_login"),
    re_path('^accounts/yandex', apiDoGet),
    re_path('signup/', CustomSignupView.as_view(), name="account_signup"),
    path('accounts/', include('allauth.urls')),

    re_path('favicon.ico', staticFiles),
    path('manifest.json', manifest),

    path('', homePage),
    path('admin/', admin.site.urls),
    # path('admin/', custom_admin.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ***

# ***

