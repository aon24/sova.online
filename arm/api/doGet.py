# -*- coding: utf-8 -*-
"""
AON 2020
"""
from arm.tools.httpMisc import notFound, jsonNotFound, accessDenied, nvResponse
from arm.settings import API_DIR, BASE_DIR, REPORT_DIR
from arm.tools.loadWell import loadWell
from arm.tools.first import err

from arm.tools.imgHeader import what
from arm.tools.DC import DC, well, swell
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
        if right == 'form':
            if request.dcUK.form in ['login']:
                return handler(request)
        if right == 'well':
            listName = request.dcUK.clues.partition('::')[0]
            if listName in ['']:
                return handler(request)

        return redirect(f'/api/login/')

    return notFound(f'api-path "{request.dcUK._path or "-?-"}" not found', request.dcUK.fullName)

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
            if not (dcUK._staff or 'куратор' in dcUK._role):
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
    return returnPageOrDoc(request, dcUK.manifest)


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

<link rel="manifest" type="application/json" href="/manifest.json">
'''


def returnPageOrDoc(request, manifest=None):
    opg = getPageObj(request)
    if not opg:
        return notFound(f'doGet.returnPageOrDoc: form "{request.dcUK.form}"', request.dcUK.fullName)

    jsDoc = opg.getJsDoc(request)

    html = well('index.html')
    html = html.replace('<title></title>', f'<title>{opg.title}</title>')
    html = html.replace('</head>', f'{opg.styles}<script>window.jsDoc={jsDoc};</script>\n</head>', 1)
    if manifest:
        html = html.replace('</title>', f'</title>{pwa}', 1)

    return nvResponse(html)

# *** *** ***


@ensure_csrf_cookie
def _loadForm(request):  # при перезагрузкe форма может исчезнуть
    js = well('form-json', request.dcUK.form)
    return nvResponse (js or '"{}"', 'application/json')

# *** *** ***

def _newForm(request):  # возможно для отладки React-form
    '''
    url: /api/get/newForm?form=myform & dbAlias=draft
    '''
    opg = getPageObj(request)
    if not opg:
        return jsonNotFound(request)
    return nvResponse(opg.getJsDoc(request), 'application/json')

# *** *** ***


def _new(request):
    '''
    url: /new?form=myform&dbAlias=dba
    '''
    if request.dcUK.form in ['v_profiles', 'v_students', 'v_schedule'] and not request.dcUK._staff:
        return accessDenied(request.dcUK.fullName)
    request.dcUK.mode = 'new'
    return returnPageOrDoc(request)

# *** *** ***


def _login(request):
    request.dcUK.mode = 'new'
    request.dcUK.form = 'arm' if request.user.is_authenticated else 'login'
    return returnPageOrDoc(request, True)

# *** *** ***


def jsv(request):
    fn = os.path.join(API_DIR, request.dcUK._query).partition('::')[0]
    fn = os.path.normpath(fn)  # Удаляет ../ и ./
    try:
        with open(fn, 'rb') as f:
            mimeType = f'{guess_type(fn, False)[0]}; charset=utf-8'
            return nvResponse('' or f.read(), mimeType, request=request)
    except:
        fn = os.path.join(REPORT_DIR, request.dcUK._query).partition('::')[0]
        fn = os.path.normpath(fn)
        try:
            with open(fn, 'rb') as f:
                mimeType = f'{guess_type(fn, False)[0]}; charset=utf-8'
                return nvResponse('' or f.read(), mimeType, request=request)
        except Exception as ex:
            err(f'jsv-path: {request.dcUK._path}\n{ex}', cat='doGet.py')
            return notFound(fn, request.dcUK.fullName)

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
                return notFound(f'not image: {path}', request.dcUK.fullName)

    except Exception as ex:
        err(f'{path}: {ex}', cat='xImage')
        return nvResponse(f'{ex}')

# *** *** ***


def _well(request):
    listName = request.dcUK.clues.partition('::')[0]
    if listName:
        k = listName.split('|')
        if not k[0].endswith('2') or request.dcUK._staff:  # студент2, etc
            ls = swell(*k)
            if type(ls) is dict:
                ls = list(ls.keys())

            return nvResponse(json.dumps(ls, ensure_ascii=False), 'application/json')

    return nvResponse('[]', 'application/json')

# *** *** ***


def _loadDoc(request):
    '''
    вызывется из xhr для показа в pageFrame
    '''
    dcUK = request.dcUK
    if dcUK.dbAlias == 'nv_Profile':
        if not (dcUK._staff or 'куратор' in dcUK._role):
            dcUK.unid = dcUK._profilePK  # cmd: openProfile withuot pk
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

@ensure_csrf_cookie
def apiRunCmd(request):
    dcUK = request.dcUK

    if dcUK.cmd == 'logout':
        logout(request)
        redirect('/')

    elif request.dcUK._staff:
        if dcUK.cmd == 'loadWell':
            loadWell('all')

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
}

# *** *** ***
