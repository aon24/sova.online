# -*- coding: utf-8 -*-
"""
AON 2020
"""
from arm.tools.httpMisc import notFound, jsonNotFound, accessDenied, nvResponse
from arm.settings import API_DIR, BASE_DIR, REPORT_DIR
from arm.tools.loadWell import loadWell
from arm.tools.first import err

from arm.tools.imgHeader import what
from arm.tools.DC import DC, well
from arm.api.forms.classPage import getPageObj
from arm.tools.dbToolkit import DJ, Book

from django.views.decorators.csrf import ensure_csrf_cookie

from django.shortcuts import redirect
from django.contrib.auth import logout

import os
import json
from mimetypes import guess_type

# *** *** ***


# @login_required(login_url='login/')
@ensure_csrf_cookie
def apiDoGet(request):

    # for k in dir(request.session):
    #     a = getattr(request.session, k)
    #     if type(a) == str:
    #         print(k, getattr(request.session, k))  # .get('csrf_token', '***************'))

    if request.method != 'GET':
        return nvResponse('Error', None, 500)

    right, handler = _apiGetList.get(request.dcUK._path, (None, None))

    if handler:
        if request.user.is_authenticated:
            return handler(request)

        if right == 'all':
            return handler(request)
        if right == 'dbAlias':
            if request.dcUK.dbAlias in ['draft', 'dba']:
                return handler(request)
        if right == 'vk':
            if 1:
                return handler(request)
        if right == 'form':
            if request.dcUK.form in ['login']:
                return handler(request)
        if right == 'well':
            listName = request.dcUK.clues.partition('::')[0]
            if listName in ['']:
                return handler(request)

        return redirect(f'/api/login/')

    err(f'api-path "{request.dcUK._path or "-?-"}" not found', cat='apiDoGet')
    return notFound(request)

# *** *** ***

def _openDoc(request):
    '''
    открывает или создает новый док нужной формы
    параметры: dbAlias+, form+, dbaGr, unidGr, smartPhone... etc
    '''

    # checkRight(dba, mode, fullName) - return accessDenied(fullName)
    dcUK = request.dcUK

    if request.dcUK.mode == 'new':
        request.dcUK.doc = DC()
    else:
        if dcUK.dbAlias == 'nv_Profile':
            if not (dcUK._staff or 'куратор' in dcUK._role or dcUK._superUser):
                dcUK.unid = dcUK._profilePK
            dcUK.unid = dcUK.unid or dcUK._profilePK

        if dcUK.dbAlias.startswith('nv_'):
            rc = DJ.docFromDB(dcUK)
        else:
            rc = Book.docFromDB(dcUK)
        if rc:
            if dcUK.mode == 'info':
                dcUK.form = 'info'
            if dcUK.form == 'info':
                if dcUK._staff:
                    dcUK.mode = 'edit'
                else:
                    dcUK.mode = 'read'

            else:
                dcUK.mode = dcUK.mode or 'read'
        else:
            s = f'Документ не найден ({dcUK._path}?{dcUK._QUERY})'
            err(s, cat='openDoc')
            dcUK.form = 'info'
            dcUK.mode = 'read'
            dcUK.doc = DC({'FORM':'info', 'ERROR': s})
    return returnPageOrDoc(request, dcUK.KEY_KEY == 'homePage')


# *** *** ***
pwa = '''
<script src="/static/home/service-worker.js"></script>

<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png"
    href="/static/home/owl192x192.png" />

<link rel="apple-touch-icon"
    href="/static/home/owl192x192.png">
<link rel="apple-touch-icon" sizes="48x48"
    href="/static/home/owl48x48.png">
<link rel="apple-touch-icon" sizes="144x144"
    href="/static/home/owl144x144.png">
<link rel="apple-touch-icon" sizes="192x192"
    href="/static/home/owl192x192.png">
<link rel="apple-touch-icon" sizes="256x256"
    href="/static/home/owl256x256.png">

<link rel="manifest" href="/static/home/manifest.json">
'''


def returnPageOrDoc(request, homePage=None):
    opg = getPageObj(request)
    if not opg:
        return notFound(f'doGet.returnPageOrDoc: form "{request.dcUK.form}"')

    jsDoc = opg.getJsDoc(request)

    html = well('groundForms', 'index')
    if opg.styles:
        html = html.replace('</head>', f'<style>{opg.styles}</style>\n</head>', 1)

    html = html.replace('<title></title>', f'<title>{opg.title}</title>')
    html = html.replace('</head>', f'<script>window.jsDoc={jsDoc};</script>\n</head>', 1)
    if homePage:
        html = html.replace('</title>', f'</title>{pwa}', 1)

    return nvResponse(html)

# *** *** ***


@ensure_csrf_cookie
def _loadForm(request):  # при перезагрузкe форма может исчезнуть
    js = well('form-json', request.dcUK.form)
    return nvResponse (js or '"{}"', 'application/json')

# *** *** ***


def vkCallback(request):
    request.dcUK.mode = 'new'
    request.dcUK.form = 'vkCallback'
    return returnPageOrDoc(request)

# *** *** ***


def callback(request):
    request.dcUK.mode = 'new'
    request.dcUK.form = 'vkCallback'
    return returnPageOrDoc(request)

# *** *** ***


def _newForm(request):  # возможно для отладки React-form
    '''
    url: /api/get/newForm?form=myform & dbAlias=draft & unid=94ec-2580-...
    '''

    # dcUK = request.dcUK
    # dcUK.doc = DC({'dbAlias': dcUK.dbAlias, 'unid': dcUK.unid, 'form': dcUK.form, 'formKey': dcUK.formKey})
    opg = getPageObj(request)
    if not opg:
        return jsonNotFound(request)
    return nvResponse(opg.getJsDoc(request), 'application/json')

# *** *** ***


def _new(request):
    '''
    url: /new?form=myform&dbAlias=dba
    '''
    request.dcUK.mode = 'new'
    request.dcUK.doc = DC({'form': request.dcUK.form})
    return returnPageOrDoc(request)

# *** *** ***


def _login(request):
    request.dcUK.mode = 'new'
    request.dcUK.form = 'login'
    return returnPageOrDoc(request, True)

# *** *** ***


def jsv(request):
    fn = os.path.join(API_DIR, request.dcUK._query).partition('::')[0].replace('..', '')
    try:
        with open(fn, 'rb') as f:
            mimeType = f'{guess_type(fn, False)[0]}; charset=utf-8'
            return nvResponse('' or f.read(), mimeType, request=request)
    except:
        fn = os.path.join(REPORT_DIR, request.dcUK._query).partition('::')[0].replace('..', '')
        try:
            with open(fn, 'rb') as f:
                mimeType = f'{guess_type(fn, False)[0]}; charset=utf-8'
                return nvResponse('' or f.read(), mimeType, request=request)
        except Exception as ex:
            err(f'jsv-path: {request.dcUK._path}\n{ex}', cat='doGet.py')
            return notFound(fn)

# *** *** ***


def xImage(request):
    try:
        dcUK = request.dcUK
        store = os.path.join(BASE_DIR, 'DB', 'files')
        path = os.path.join(store, dcUK.path)
        mimeType = dcUK.type

        with open(path, 'rb') as f:
            if what(path):
                return nvResponse(f.read(), content_type=mimeType, request=request)
            else:
                return notFound(f'not image: {path}')

    except Exception as ex:
        err(f'{path}: {ex}', cat='xImage')
        return nvResponse(f'{ex}')

# *** *** ***


def _well(request):
    listName = request.dcUK.clues.partition('::')[0]
    ls = listName and well(*listName.split('|'))
    if type(ls) is dict:
        ls = list(ls.keys())

    return nvResponse(json.dumps(ls or [], ensure_ascii=False), 'application/json')

# *** *** ***


def _loadDoc(request):
    '''
    вызывется из xhr для показа в pageFrame
    '''
    dcUK = request.dcUK
    if dcUK.dbAlias == 'nv_Profile':
        if not (dcUK._staff or 'куратор' in dcUK._role or dcUK._superUser):
            dcUK.unid = dcUK._profilePK
        dcUK.unid = dcUK.unid or dcUK._profilePK

    if dcUK.dbAlias.startswith('nv_'):
        doc = DJ.docFromDB(dcUK)
    else:
        doc = Book.docFromDB(dcUK)

    if doc:
        opg = getPageObj(request)
        if opg:
            return nvResponse(opg.getJsDoc(request), 'application/json')

        err(f'form not found\n{dcUK}', cat='_loadDoc')
        return nvResponse(f'form not found\n{dcUK}', status=400)

    s = f'Документ не найден ({dcUK._path}?{dcUK._QUERY})'
    err(s, cat='_loadDoc')
    dcUK.form = 'info'
    dcUK.mode = 'read'
    dcUK.doc = DC({'FORM':'info', 'ERROR': s})
    opg = getPageObj(request)
    return nvResponse(opg.getJsDoc(request), 'application/json')

# *** *** ***


def _getData(request):
    '''
    вызывется из xhr для загрузки каких-либо данных
    '''
    opg = getPageObj(request)
    if opg:
        s = opg.getData(request.dcUK)
        if s:  # s м.б. HttpResponse
            return nvResponse(s, 'application/json') if type(s) is str else s
        err(f'Invalid data for URL:"{request.path}?{request.dcUK._query}"', cat='_getData')
        return nvResponse('Error', status=400)

    s = f'form "{request.dcUK.form}" not found'
    err(s, cat='_getData')
    return nvResponse(json.dumps(s), 'application/json', status=400)


# *** *** ***
from DB.workers import loadNV, exportEmail


@ensure_csrf_cookie
def apiRunCmd(request):
    dcUK = request.dcUK
    if dcUK.cmd == 'openPage':
        try:
            with open(os.path.join(BASE_DIR, 'arm', 'html', dcUK.file), 'rb') as f:
                return nvResponse(f.read())
        except Exception as ex:
            err(f'{dcUK.file}\n{ex}', cat='openPage')
            return nvResponse(f'{ex} status=400')

    if dcUK.cmd == 'logout':
        logout(request)
        redirect('/')
    elif dcUK.cmd == 'loadNV':
        loadNV()
    elif dcUK.cmd == 'loadWell':
        loadWell('all')
    elif dcUK.cmd == 'exportEmail':
        exportEmail()

    return nvResponse('"ok"', 'application/json')

_apiGetList = {
    # no authenticated
    'xImage': ('all', xImage),
    'jsv': ('all', jsv),
    'loadForm': ('all', _loadForm),
    'login': ('all', _login),
    # no authenticated for draft/dba
    'opendoc': ('dbAlias', _openDoc),
    'new': ('dbAlias', _new),
    'newForm': ('dbAlias', _newForm),
    'loadDoc': ('dbAlias', _loadDoc),
    # no authenticated only for ...
    'well': ('well', _well),
    'getData': ('form', _getData),
    # authenticated need
    'runCmd': (None, apiRunCmd),
    'vkcallback': ('vk', vkCallback),
    'callback': ('all', callback),
}

# *** *** ***
