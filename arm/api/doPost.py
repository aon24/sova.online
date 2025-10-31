# -*- coding: utf-8 -*-
"""
AON 2020

"""
from arm.settings import BASE_DIR, DEMO_MODE
from arm.tools.httpMisc import accessDenied, nvResponse
from arm.tools.DC import DC, swell, toSwell
from arm.tools.loadWell import loadWell
from arm.tools.first import err, snd
from arm.api.forms.classPage import getPageObj
from arm.tools.dbToolkit import DJ, Book

from nv.admin import getModel

from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import redirect
from django.contrib.auth import logout

import json
import os
import zlib

# *** *** ***


@ensure_csrf_cookie
def doPost(request, buf):

    # ***

    def _saveDoc():
        cat = 'doPost.py.saveDoc'

        oldF, newF = {}, {}
        script = None
        for k, v in buf.items():
            if k == 'THESCRIPT':
                script = zlib.compress(v[1].encode(), 9)
                newF[k] = 'saved'
            else:
                oldF[k], newF[k] = v

        oldPage = dcUK.unid and dcUK.loadDoc()  # возвращает запись(модель типа Page для dcUK.dbAlias == 'draft')

        # check right in dcUK old doc
        if not checkRight(dcUK, saveDoc=True):
            return accessDenied(request)

        # ***

        if script:
            try:
                path = os.path.join(BASE_DIR, 'DB', 'scripts', dcUK.fullName.partition(' ')[0] or 'guest')
                os.makedirs(path, exist_ok=True)

                with open(os.path.join(path, dcUK.unid), 'bw') as f:
                    f.write(script)
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
            if opg and not opg.afterSave(dcUK, mmm.id):
                return nvResponse('AfterSave error', status=400)
            return nvResponse(f'OK|{mmm.id}')
        else:
            if opg and not opg.afterSave(dcUK):
                return nvResponse('AfterSave error', status=400)
            return nvResponse(f'OK|{dcUK.doc.unid}')

    # *** *** ***

    '''
    вызывется из xhr для загрузки каких-либо данных
    '''

    def _newForm():
        opg = getPageObj(request)
        if opg:
            return nvResponse(opg.getJsDoc(request), 'application/json')
        err(f'form not found\n{dcUK}', cat='_loadDoc')
        return nvResponse(f'form not found\n{dcUK}', status=400)

    # ***

    def _loadDoc():
        if dcUK.dbAlias == 'nv_Profile':
            if not (dcUK._staff or 'куратор' in dcUK._role):
                dcUK.unid = dcUK._profilePK  # cmd: openProfile withuot pk
            dcUK.unid = dcUK.unid or dcUK._profilePK

        if dcUK.dbAlias.startswith('nv_'):
            doc = DJ.docFromDB(dcUK)
        else:
            doc = Book.docFromDB(dcUK)

        if doc:
            if dcUK.dbAlias == 'nv_SessionSt':
                if not (dcUK._staff or 'куратор' in dcUK._role):
                    if dcUK._profilePK != doc.pref or not dcUK.doc.allow_s:
                        return nvResponse(b'', status=403)

            opg = getPageObj(request)
            if opg:
                return nvResponse(opg.getJsDoc(request), 'application/json')

            err(f'form not found\n{dcUK}', cat='_loadDoc')
            return nvResponse(f'form not found\n{dcUK}', status=400)

        s = f'Документ не найден ({dcUK._path}?{dcUK._QUERY})'
        err(s, cat='_loadDoc')
        dcUK.form = 'info'
        dcUK.mode = 'read'
        dcUK.doc = DC({'FORM': 'info', 'ERROR': s})
        opg = getPageObj(request)
        return nvResponse(opg.getJsDoc(request), 'application/json')

    # ***

    def _loadHtml():  # ./static/html/helpStudent.html
        html = swell(dcUK.filePath)
        if not html:
            try:
                with open(os.path.join(BASE_DIR, 'static', 'html', dcUK.filePath), encoding='utf-8') as f:
                    html = f.read()
                    toSwell(html, dcUK.filePath)
            except Exception as ex:
                html = f'{dcUK.filePath}: {ex}'
                err(html, cat='htmlField')
        return nvResponse(html)

    # ***

    def _getData():
        opg = getPageObj(request)
        if opg:
            dcUK.buf = buf
            s = opg.getData(dcUK)
            if s:  # s м.б. HttpResponse
                return nvResponse(s, 'application/json') if type(s) is str else s

        s = f'form "{dcUK.form}" or cmd "{dcUK.cmd}" not found'
        err(s, cat='doPost.getData')
        return nvResponse(s, status=404)

    # ***

    def _copyDoc():
        cat = 'doPost.copyDoc'
        try:
            mmm, mmn = getModel(dcUK, cat)
            if mmm:
                oldDoc = mmm.docs.get(pk=dcUK.pk)
                fields = {fn: value for fn, value in oldDoc if fn not in ['id', 'full_name', 'title']}

                newDoc = mmm(**fields)
                newDoc.save()
                snd(f'table={mmn}(pk={dcUK.pk})', cat=cat)
                loadWell(mmn)
                return nvResponse('OK')

            err(f'invalid model: {dcUK.dbAlias}', cat=cat)
            return nvResponse(f'invalid model: {dcUK.dbAlias}')

        except Exception as ex:
            err(f'{ex}', cat=cat)
            return nvResponse(f'{ex}')

    # ***

    def _deleteFromDB():
        cat = 'doPost.deleteFromDB'

        if not checkRight(dcUK):
            return accessDenied(request)

        if not dcUK.loadDoc():
            err(f'Документ уже удален: "{dcUK.dbAlias}:{dcUK.unid}" {dcUK.fullName}', cat=cat)
            return nvResponse('Документ уже удален', status=410)

        dcUK.doc.status = 'deleted'
        if dcUK.save():
            snd(f'table={dcUK.dbAlias}(pk={dcUK.unid}). Eraser:{dcUK.fullName}', cat=cat)
            model = getModel(dcUK, cat)[1] or 'Landing'
            loadWell(model)
            return nvResponse('OK')

        else:
            err(f'Ошибка записи в базу: "{dcUK.dbAlias}:{dcUK.unid}" {dcUK.fullName}', cat=cat)
            return nvResponse('Ошибка записи в базу', status=411)

    # ***

    def _well():
        listName = dcUK.clues.partition('::')[0]
        ls = []
        if listName:
            k = listName.split('|')
            if not k[0].endswith('2') or dcUK._staff or 'куратор' in dcUK._role or 'преподаватель' in dcUK._role:  # студент2, etc
                ls = swell(*k)
                if type(ls) is dict:
                    ls = list(ls.keys())

        return nvResponse(json.dumps(ls, ensure_ascii=False), 'application/json')

    # ***

    def _logout():
        logout(request)
        redirect('/')
        return nvResponse('OK')

    def _loadWell():
        request.dcUK._staff and loadWell('all')
        return nvResponse('OK')

    # *** *** ***
    # *** *** ***

    dcUK = request.dcUK
    if dcUK._path != 'getJson':
        return accessDenied(request)

    # единственное, что может незарегистрированный - это зарегистрироваться(форма signup)
    if not (request.user.is_authenticated or (dcUK.form == 'signup' and not dcUK.dbAlias)):
        if not DEMO_MODE:
            return accessDenied(request)

    # вызываем то, что в dcUK.cmd или getData для формы
    return {
            'saveDoc': _saveDoc,
            'newForm': _newForm,
            'loadDoc': _loadDoc,
            'loadHtml': _loadHtml,
            'copyDoc': _copyDoc,
            'deleteFromDB': _deleteFromDB,
            'logout': _logout,
            'well': _well,
            'loadWell': _loadWell,
        }.get(dcUK.cmd, _getData)()

# *** *** ***

# *** *** ***


def checkRight(dcUK, saveDoc=None):
    if DEMO_MODE:
        return True

    if dcUK._staff or 'куратор' in dcUK._role:
        return True

    if dcUK.dbAlias == 'nv_Profile' and dcUK.doc and dcUK._profilePK == dcUK.doc.id:  # может править свой профайл
        return True

    elif 'преподаватель' in dcUK._role:
        if dcUK.dbAlias == 'nv_SessionTmpl':  # может править с-тмпл
            return True

    if saveDoc and dcUK.doc:  # может править толко с-ст и только свою
        if dcUK.dbAlias == 'nv_SessionSt' and dcUK.doc.pref == dcUK._profilePK:
            return True

# *** *** ***
