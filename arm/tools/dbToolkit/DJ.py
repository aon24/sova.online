# -*- coding: utf-8 -*-

from arm.tools.common import now
from arm.tools.first import err, snd
from arm.tools.DC import DC, getRoot
from nv.admin import getModel, all_ml, model_names, model_fields

import json
import zlib, base64
import datetime

# *** *** ***

ZIPLEN = 5000

# *** *** ***

def docFromDB(dcUK):
    """
    возвращает документ по unid. unid - pk
    если unid пустой возвращает по знчению ключей
    """

    cat = 'docFromDB'
    if not dcUK.unid or dcUK.unid == 'new':
        return err(f'empty unid', cat=cat)

    mmm, mmmName = getModel(dcUK, cat)
    if not mmm:
        err(f'doc not loaded. Invalid model: {dcUK.query}', cat=cat)
        return

    # ***
    try:
        dbDoc = mmm.docs.get(pk=int(dcUK.unid))
        # dbDoc = mmm.docs.values().get(pk=int(dcUK.unid))
    except:
        err(f'doc not found: {dcUK.dbAlias}:{dcUK.unid}', cat=cat)
        return

    dcUK.doc = DC()
    try:
        dbFields = model_fields[mmmName][0]
        for fn in dbFields:
            value = getattr(dbDoc,fn,None)
            if not value:
                continue

            if fn in model_names:
                dcUK.doc[fn] = dcUK.doc[f'{fn}_id'] = value.id
            elif fn == 'body':
                getRoot(dcUK.doc, value)
            elif type(value) is datetime.date:
                dcUK.doc[fn] = value
            elif type(value) is datetime.datetime:
                if fn.startswith('date_'):
                    dcUK.doc[fn] = value.strftime('%Y-%m-%d')
                else:
                    dcUK.doc[fn] = value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                dcUK.doc[fn] = value
        return dbDoc

    except Exception as ex:
        err(f'{dcUK.query}\n{ex}', cat=cat)

# *** *** ***


def docSaveDB(dcUK, dbDoc=None):
    '''
    dcUK.doc - документ, который нужно записать
    oldDoc - запись в базе с существующим документом, котрую нужно перевести в истоию.
    '''
    cat = 'docSaveDB'
    mmm, mmmName = getModel(dcUK, cat)
    if not mmm:
        err(f'doc not saved. Invalid model: {dcUK.dbAlias}', cat=cat)
        return

    if not dbDoc:
        if dcUK.unid and dcUK.unid != 'new':
            try:
                dbDoc = mmm.docs.get(pk=int(dcUK.unid))  # есть такой, - переводим в историю
                created = None
            except Exception as ex:
                err(f'doc not found: {dcUK.dbAlias}:{dcUK.unid}:{ex}', cat=cat)
                return
        else:
            dbDoc = mmm()
            created = True

    # сохраняем новый док(или новую версию)
    body = {}
    dbFields = model_fields[mmmName][0]
    dbFields_id = model_fields[mmmName][1]
    try:
        for k, v in dcUK.doc.items():
            lofi = k.lower()
            if lofi == 'id':
                setattr(dbDoc, 'id', int(v))
            elif lofi in dbFields:
                if not created:
                    exv = getattr(dbDoc, lofi, None)
                    if exv == v:
                        continue

                if lofi in all_ml:  # если название поля входит в список моделей
                    if v:
                        setattr(dbDoc, lofi, all_ml[lofi](int(v)))
                    else:
                        setattr(dbDoc, lofi, None)
                else:
                    setattr(dbDoc, lofi, v or None)
            elif lofi not in dbFields_id:  # не записывать 'pref_id', 'status_id', 'body_id'...
                body[k] = v

        if body:
            if created:
                body['_CREATED'] = now('-')
                body['_CREATOR'] = dcUK.fullName
            else:
                body['_MODIFIED'] = now('-')
                body['_MODIFIER'] = dcUK.fullName

            js = json.dumps(body, ensure_ascii=False)
            if len(js) > ZIPLEN:
                by = zlib.compress(js.encode(), 9)
                bo = str(base64.b64encode(by), 'ascii')
                lenjs = len(js)
                lenbo = len(bo)
                le = f'fullsize:{lenjs} => zip => b64:{lenbo}'
                proc = int(100 * lenbo / lenjs)
                setattr(dbDoc, 'body', bo)
                snd(f'{le} (doc {dcUK.unid} in "{dcUK.dbAlias}") press:{proc}%', cat='ROOT-size')
            else:
                setattr(dbDoc, 'body', js)

        dbDoc.save()
        # snd(f'id={dbDoc.id} in "{dcUK.dbAlias}"(UN={dcUK.fullName})', cat='docSaveDB')
        return dbDoc

    except Exception as ex:
        err(f'doc not saved: {ex} (UN={dcUK.fullName})', cat=cat)
        # print(dcUK.doc)

# *** *** ***
