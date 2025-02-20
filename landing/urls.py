from django.urls import path
import arm.api.doGet as doGet


def callArm(request):  # открыть АРМ при входе на сайт
    request.dcUK.path = 'opendoc'
    request.dcUK.mode = 'new'
    request.dcUK.form = 'arm'

    return doGet.apiDoGet(request)


urlpatterns = [path(r'', callArm)]

