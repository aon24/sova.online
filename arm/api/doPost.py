# -*- coding: utf-8 -*-
"""
AON 2020

"""
from arm.settings import BASE_DIR
from arm.tools.httpMisc import accessDenied, nvResponse
from arm.tools.DC import DC
from arm.tools.loadWell import loadWell
from arm.tools.first import err, snd
from arm.api.forms.classPage import getPageObj

from nv.admin import getModel

from django.views.decorators.csrf import ensure_csrf_cookie

import json
import os
import zlib

# *** *** ***


@ensure_csrf_cookie
def doPost(request):
    try:
        handler = _keysApiPost.get(request.dcUK._path, None)

        if handler and request.user.is_authenticated:
            ln = int(request.META.get('CONTENT_LENGTH', -1))
            buf = request.META['wsgi.input'].read(ln).decode()
            return handler(request, buf)
        else:
            err(f'POST error for "{request.dcUK._path}"', cat='doPost')
            return accessDenied(request)
    except Exception as ex:
        err(f'POST error for "{request.dcUK._path}": {ex}', cat='doPost')
        return nvResponse(f'POST error for "{request.dcUK._path}": {ex}', status=500)


def errAD(request):
    err(f'"{request.dcUK._path}": {request.dcUK.fullName}(Role:{request.dcUK._role})', cat='doPost-AD')
    return accessDenied(request)


def checkRight(dcUK, student=None):
    # dbAlias=${this.dbAlias}&unid=${this.unid}&form=${this.form}

    if dcUK._staff or 'куратор' in dcUK._role:
        return True

    elif 'преподаватель' in dcUK._role:
        if dcUK.dbAlias == 'nv_c_Profile':  # может править свой профайл
            if dcUK._profilePK == dcUK.unid:
                return True
        elif dcUK.dbAlias == 'nv_SessionTmpl':  # может править с-тмпл
            return True

    elif student and dcUK.doc and 'студент' in dcUK._role:  # может править толко с-ст и только свою
        if dcUK.dbAlias == 'nv_SessionSt' and dcUK.doc.pref == dcUK._profilePK:
            return True

# *** *** ***


def apiSaveDoc(request, buf):
    dcUK = request.dcUK

    cat = 'doPost.py.saveDoc'
    try:
        jsonO = json.loads(buf)
    except Exception as ex:
        s = f'Except by save: json.loads(): \n{ex}\n{buf[:100]}'
        err(s, cat=cat)
        return nvResponse(s, status=400)

    oldF, newF = {}, {}
    r = None
    for k, v in jsonO.items():
        if k == 'THESCRIPT':
            r = zlib.compress(v[1].encode(), 9)
            newF[k] = 'saved'
        else:
            oldF[k], newF[k] = v

    oldPage = dcUK.unid != 'new' and dcUK.loadDoc()  # возвращает запись(модель типа Page для dcUK.dbAlias == 'draft')

    # check right in dcUK old doc
    if not checkRight(dcUK, student=True):
        return errAD(request)


    # ***

    # dcUK.unid = newF['UNID'] = newF.get('UNID', uuid.uuid4().hex)
    if r:
        try:
            path = os.path.join(BASE_DIR, 'DB', 'scripts', dcUK.fullName.partition(' ')[0] or 'guest')
            os.makedirs(path, exist_ok=True)

            with open(os.path.join(path, dcUK.unid), 'bw') as f:
                f.write(r)
        except Exception as ex:
            err(f'the script saved error: {ex}', cat=cat)

    # if not (('EMAIL' not in newF) or emailValidator(newF['EMAIL']) or dcUK.force):
    #     return f"В поле E_MAIL недействительный эл. адрес:\n\n{newF['EMAIL']}", None, 449

    # oldPage = None

    if oldPage:
        if not dcUK.force:
            mdf = dcUK.doc._MODIFIER

            if 'FROMHIST' in newF:  # FROMHIST - всегда даст конфликт
                del newF['FROMHIST']
            else:
                for k in oldF:
                    if k not in ['ROOT', '_MODIFIED', '_MODIFIER', 'THESCRIPT']:
                        of = dcUK.doc[k]
                        if oldF[k] != of and newF.get(k, '') != of:
                            s = f'''ИМЯ ПОЛЯ: {k}
    НОВОЕ ЗНАЧЕНИЕ: "{newF.get(k, '')}"
    СТАРОЕ ЗНАЧЕНИЕ: "{oldF[k]}"
    КОНФЛИКТНОЕ ЗНАЧЕНИЕ: "{of}"
    ИЗМЕНЕНО: {dcUK.doc.MODIFIED or '- ? -'}
    РЕДАКТОР: {mdf or '- ? -'}'''
                            err(s, cat=cat)
                            return nvResponse(s, status=409)

            if mdf and mdf != dcUK.fullName and oldF.get('ROOT', '') != dcUK.doc.ROOT:
                s = f'''ИМЯ ПОЛЯ: 'ROOT'
НОВОЕ ЗНАЧЕНИЕ (размер): {len(newF.get('ROOT', ''))}
СТАРОЕ ЗНАЧЕНИЕ (размер): {len(oldF.get('ROOT', ''))}
КОНФЛИКТНОЕ ЗНАЧЕНИЕ (размер): {len(dcUK.doc.ROOT)}
ИЗМЕНЕНО: {dcUK.doc.MODIFIED or '- ? -'}
РЕДАКТОР: {mdf}'''
                err(s, cat=cat)
                return nvResponse(s, status=409)

        for k, v in dcUK.doc.items():
            if k not in newF:  # в newF только изменения, добавляем в него неизмененные поля
                newF[k] = v

        newF['FORM'] = newF.get('FORM') or dcUK.doc.form
        # костыль для заполнения форм после загрузки базы из скрипта

    # v = json.loads(newF['ROOT'])
    # for i in range(10):
        # v = v.get('boxes')
        # if not v:
            # break
        # if not len(v):
            # break
        # v = v[0]
        # t = v.get('tuning')
        # if t.get('wall'):
            # for k, vv in t.items():
                # print('tuning:', k, vv)
            # t = v.get('rect')
            # for k, vv in t.items():
                # print('rect', k, vv)
            # break
    # return

    newF['FORM'] = newF.get('FORM') or dcUK.form
    # костыль для заполнения форм после загрузки базы из скрипта

    dcUK.doc = DC(newF)
    opg = getPageObj(request)

    if opg:
        if not opg.querySave(dcUK):
            err(f'BeforeSave error, Form={dcUK.form}', cat=cat)
            return nvResponse('BeforeSave error', status=400)

    if dcUK.doc.noSave:
        return nvResponse('OK|noSave')

    mmm = dcUK.save()
    if not mmm:  # mmm - Model for DJango or True for a_design
        return nvResponse('DocSave error', status=400)

    if dcUK.dbAlias.startswith('nv_'):
        if opg and not opg.afterSave(dcUK, mmm.pk):
            return nvResponse('AfterSave error', status=400)
        return nvResponse(f'OK|{mmm.pk}')
    else:
        if opg and not opg.afterSave(dcUK):
            return nvResponse('AfterSave error', status=400)
        return nvResponse(f'OK|{dcUK.unid}')

# *** *** ***


def deleteFromDB(request, buf=None):
    cat = 'doPost.deleteFromDB'
    dcUK = request.dcUK

    if not checkRight(dcUK):
        return errAD(request)

    dcUK.unid = dcUK.unid or dcUK.pk
    if not dcUK.loadDoc():
        err(f'Документ уже удален: "{dcUK.dbAlias}:{dcUK.unid}"', cat=cat)
        return 'Документ уже удален', None, 410

    dcUK.doc.status = 'deleted'
    if dcUK.save():
        snd(f'table={dcUK.dbAlias}(pk={dcUK.unid})', cat=cat)
        model = getModel(dcUK, cat)[1] or 'Landing'
        loadWell(model)
        return nvResponse('OK')

    else:
        err(f'Ошибка записи в базу: "{dcUK.dbAlias}:{dcUK.unid}"', cat=cat)
        return 'Ошибка записи в базу', None, 411

# *** *** ***


def create(request, buf):
    dcUK = request.dcUK

    # check right
    if not checkRight(dcUK):
        return errAD(request)

    # ***

    cat = 'doPost.create'
    try:
        mmm, mmn = getModel(dcUK, cat)
        if mmm:
            fields = dict(
                status='active',
            )
            mmm.objects.create(**fields)
            snd(f'table={mmn}', cat=cat)
            loadWell(mmn)
            return nvResponse('OK')

        err(f'invalid model: {dcUK.dbAlias}', cat=cat)
        return nvResponse(f'invalid model: {dcUK.dbAlias}')
    except Exception as ex:
        err(f'{ex}', cat=cat)
        return nvResponse(f'{ex}')

# *** *** ***

def putData(request, buf):
    '''
    вызывется из xhr для загрузки каких-либо данных
    '''
    opg = getPageObj(request)
    if opg:
        return opg.putData(request.dcUK, buf)

    s = f'form "{request.dcUK.form}" not found'
    err(s, cat='doPost.putData')
    return nvResponse(s)

# *** *** ***

_keysApiPost = {
    'putData': putData,
    'deleteFromDB': deleteFromDB,
    'saveDoc': apiSaveDoc,
    'create': create,
}

# *** *** ***

