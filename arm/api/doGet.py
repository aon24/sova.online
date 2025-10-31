# -*- coding: utf-8 -*-
"""
AON 2020
"""
from arm.tools.httpMisc import notFound, accessDenied, nvResponse
from arm.settings import BASE_DIR, DB_DIR
from arm.tools.first import err
from arm.tools.imgHeader import what
from arm.tools.DC import DC, well, config
from arm.api.forms.classPage import getPageObj
from arm.tools.dbToolkit import DJ, Book

from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import redirect

import os
from mimetypes import guess_type

# *** *** ***


# @login_required(login_url='login/')
@ensure_csrf_cookie
def apiDoGet(request):
    right, handler = _apiGetList.get(request.dcUK._path, (None, None))

    if handler:
        if request.user.is_authenticated:
            return handler(request)

        if right == 'all':
            return handler(request)
        if right == 'dbAlias':
            if request.dcUK.dbAlias in ['draft', 'dba', 'etc']:
                return handler(request)
        if right == 'form':
            if request.dcUK.form in ['login']:
                return handler(request)
        if right == 'well':
            listName = request.dcUK.clues.partition('::')[0]
            if listName in ['q']:
                return handler(request)

        return redirect('/api/login/')

    return notFound(request)

# *** *** ***


def _openDoc(request):
    '''
    открывает или создает новый док нужной формы
    параметры: dbAlias+, form+, dbaGr, unidGr, smartPhone... etc
    '''

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

            if dcUK.dbAlias == 'nv_SessionSt':
                if not (dcUK._staff or 'куратор' in dcUK._role):
                    if dcUK._profilePK != dcUK.doc.pref or not dcUK.doc.allow_s:
                        return nvResponse(b'', status=403)

        else:
            s = f'Документ не найден ({dcUK._path}?{dcUK._QUERY})'
            err(s, cat='openDoc')
            dcUK.form = 'info'
            dcUK.mode = 'read'
            dcUK.doc = DC({'FORM': 'info', 'ERROR': s})
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
        return notFound(request)

    jsDoc = opg.getJsDoc(request, config.coocieBtn)

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
    return nvResponse(js or '"{}"', 'application/json')

# *** *** ***


def _new(request):
    '''
    url: /new?form=myform&dbAlias=dba
    '''
    if request.dcUK.form in ['v_profiles', 'v_students', 'v_schedule'] and not request.dcUK._staff:
        return accessDenied(request)
    request.dcUK.mode = 'new'
    request.dcUK.form = request.dcUK.form or 'arm'
    return returnPageOrDoc(request)

# *** *** ***


def _login(request):
    request.dcUK.mode = 'new'
    if request.user.is_authenticated:
        request.dcUK.form = 'arm'
        manifest = None
    else:
        request.dcUK.form = 'login'
        manifest = True
    return returnPageOrDoc(request, manifest)

# *** *** ***


def jsv(request):
    if request.dcUK._query.startswith('forms/'):
        fn = os.path.join(BASE_DIR, 'arm', 'api', request.dcUK._query).partition('::')[0]
    else:
        fn = os.path.join(BASE_DIR, request.dcUK._query).partition('::')[0]
    fn = os.path.normpath(fn)  # Удаляет ../ и ./
    try:
        with open(fn, 'rb') as f:
            mimeType = f'{guess_type(fn, False)[0]}; charset=utf-8'
            return nvResponse(f.read(), mimeType, request=request)
    except Exception as ex:
        err(f'jsv-path: {request.dcUK._path}\n{ex}', cat='doGet.py')
        return notFound(request)

# *** *** ***


def xImage(request):
    try:
        dcUK = request.dcUK
        store = os.path.join(DB_DIR, 'files')
        path = os.path.join(store, dcUK.path)
        mimeType = dcUK.type

        with open(path, 'rb') as f:
            if what(path):
                return nvResponse(f.read(), content_type=mimeType, request=request)
            else:
                return notFound(request)

    except Exception as ex:
        err(f'{path}: {ex}', cat='xImage')
        return nvResponse(f'{ex}')

# *** *** ***


_apiGetList = {
    # no authenticated
    'xImage': ('all', xImage),
    'jsv': ('all', jsv),
    'loadForm': ('all', _loadForm),
    'login': ('all', _login),
    # no authenticated for draft/dba
    'opendoc': ('dbAlias', _openDoc),
    'new': ('dbAlias', _new),
}

# *** *** ***
