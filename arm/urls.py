from arm.api.doGet import apiDoGet
<<<<<<< HEAD
from arm.views import CustomSignupView, CustomLoginView, rsApi, download_file, staticFiles, home, homePage, manifest
=======
from arm.views import CustomSignupView, CustomLoginView, rsApi, download_file, staticFiles, home, homePage
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770
from arm.tools.first import snd
from arm.tools.amgr import amgrLoop
from arm.tools.loadWell import loadWell

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include

# Единственное место в Джанго, где можно настроить приложение 1 раз
import threading

snd('=== Server started ===', cat='logging')
loadWell('all')
threading.Thread(target=amgrLoop).start()
snd('Amgr starts as new Thread.', cat='amgr')

# ***

handler404 = 'arm.views.custom_404_view'

urlpatterns = [
    re_path('^api/signup', CustomSignupView.as_view(), name="account_signup"),
    re_path('^api/', rsApi),

    re_path('^image/', staticFiles),
    re_path('^static/', staticFiles),  # in DEBUG-mode работает странно: подключает свои обработчики
    re_path('^download/', download_file),

    re_path('login/', CustomLoginView.as_view(), name="account_login"),
    re_path('^accounts/yandex', apiDoGet),
    re_path('signup/', CustomSignupView.as_view(), name="account_signup"),
    path('accounts/', include('allauth.urls')),


    path('', homePage),
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    re_path('^manifest.json', manifest),

    # *.html, favicon.ico,manifest.json,robots.txt,sitemap.xml
    re_path(r'.*\.(html|txt|ico|xml|js|json|css|png)$', home),

=======
    path('favicon.ico', home),
    path('manifest.json', home),
    path('robot.txt', home),
    path('sitemap.xml', home),
>>>>>>> 2d0df3faef32214b0a2de7e9081ee69fdf60e770
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ***

# ***

