from arm.tools.common import now, sndErr
from arm.tools.first import err, snd
from arm.tools.DC import DC, well
from arm.settings import DB_DIR


import json
import zlib, base64
from datetime import datetime
import os
import sqlite3 as sqldb
import time
from contextlib import suppress
import threading
import uuid

# *** *** ***


@sndErr
def createDB(dba, *addPath):
    cat = 'createDB'
    dbAlias = tableName(dba)

    path = os.path.join(DB_DIR, *addPath)
    os.makedirs(path, exist_ok=True)
    dbFile = os.path.join(path, f'{dbAlias}.rsf')

    con = sqldb.connect(database=dbFile, timeout=10.0)
    con.create_collation("casei", sqlite_collation_casei)
    con.create_function("sqLike", 2, sqlite_function_sqLike)

    sql = """CREATE TABLE "LIFE" (
"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
"unid" char(32) NOT NULL,
"xfld" text NOT NULL,
"xmdf" timestamp NULL);

CREATE INDEX "LIFE_unid" ON "LIFE" ("unid");
CREATE INDEX "LIFE_xmdf" ON "LIFE" ("xmdf");
"""
    cur = con.cursor()

    for s in sql.split(';\n'):
        s and cur.execute(s)

    with suppress(Exception):
        cur.close()
        con.commit()
        con.close()

    snd(f'Created database "{dbFile}"', cat=cat)
    return True

# *** *** ***


def tableName(dbAlias):
    return dbAlias.replace('.', '/').upper()


def sqlite_collation_casei(x, y):
    _x = x.lower()
    _y = y.lower()
    return 0 if _x == _y else -1 if _x < _y else 1


def sqlite_function_sqLike(s, patt):
    _patt = patt.lower().replace('%', '')
    _s = s.lower()
    if patt[0] == '%' and patt[-1] == '%':
        return _patt in _s
    elif patt[0] == '%':
        return _s.endswith(_patt)
    elif patt[-1] == '%':
        return _s.startswith(_patt)
    else:
        return _s == _patt

# *** *** ***


def hasDB(dbAlias):
    dbFile = os.path.join(DB_DIR, f'{tableName(dbAlias).upper()}.rsf')
    return os.path.isfile(dbFile) and os.stat(dbFile).st_size

# *** *** ***


def connectToSrv(dba):
    dbAlias = tableName(dba)
    dbFile = os.path.join(DB_DIR, f'{dbAlias}.rsf')

    if os.path.isfile(dbFile) and os.stat(dbFile).st_size:
        if lockupConnect(dbAlias):
            con = sqldb.connect(database=dbFile, timeout=10.0)
            con.create_collation("casei", sqlite_collation_casei)
            con.create_function("sqLike", 2, sqlite_function_sqLike)
            return con
        else:
            err(f'SQLITE: DB "{dbFile}" is locked', cat='Book.connectToSrv')
            return
    else:
        raise Exception(f'SQLITE: DB "{dbFile}" not found')

# *** *** ***


lockedCon = {}


def lockupConnect(dbAlias):
    if dbAlias not in lockedCon:
        lockedCon[dbAlias] = threading.Lock()
        lockedCon[dbAlias].acquire()
        return True

    for n in range(100):
        try:
            if dbAlias not in lockedCon or lockedCon[dbAlias].acquire(False):
                return True
        except:
            return True
        time.sleep(0.1)


def unlockCon(con, dbAlias):
    with suppress(Exception):
        con.close()
    try:
        lockedCon[tableName(dbAlias)].release()
        del lockedCon[tableName(dbAlias)]
    except:
        pass


def unlockAll():
    global lockedCon
    for l in lockedCon.items():
        l.release()
    lockedCon = {}

# *** *** ***


def docFromDB(dcUK):
    """
    возвращает документ по unid. unid - текстовый hex
    если unid пустой возвращает по знчению ключей
    """

    if not dcUK.unid:
        dcUK.doc = well('landingByPage', dcUK.page.lower())
        return dcUK.doc

    # ***

    try:
        unid = dcUK.unid.replace('-', '')

        if dcUK.xmdf:
            xmdf = f"xmdf='{dcUK.xmdf}'"  # get history
        else:
            xmdf = 'xmdf IS NULL'

        sql = f"SELECT xfld FROM LIFE WHERE (unid='{unid}') AND ({xmdf});"

        con = connectToSrv(dcUK.dbAlias)
        if not con:
            return

        cur = con.cursor()
        cursor = cur and cur.execute(sql)
        if not cursor:
            cur and cur.close()
            unlockCon(con, dcUK.dbAlias)
            return

        xfld = None
        for row in cursor:
            xfld = row[0]

        cur.close()
        unlockCon(con, dcUK.dbAlias)

        if not xfld:
            return

        fields = json.loads(xfld)
        fields['UNID'] = unid
        if 'ROOT' in fields:
            root, _, styles = fields['ROOT'].partition('_¤_')
            fields['ROOT'] = zlib.decompress(base64.b64decode(root)).decode()
            styles = styles and zlib.decompress(base64.b64decode(styles)).decode()
            styles = (styles + ('_¤_' * 9)).split('_¤_')
            for i in range(9):
                if styles[i]:
                    fields[f'ROOT_STYLES_{(i+1)*1000}'] = styles[i]
        dcUK.doc = DC(fields)
        return True

    except Exception as ex:
        err(f'dbAlias={dcUK.dbAlias}&unid={unid}\n{ex}', cat='Book.docFromDB')

# *** *** ***


def docSaveDB(dcUK):
    '''
    dcUK.doc - документ, который нужно записать
    oldDoc - запись в базе с существующим документом, котрую нужно перевести в истоию.
    '''

    unid = dcUK.unid
    if unid:
        old = DC({'dbAlias': dcUK.dbAlias, 'unid': unid})
        oldDoc = docFromDB(old)
    else:  # new doc
        oldDoc = None
        unid = dcUK.doc.unid = uuid.uuid4().hex

    if oldDoc:  # есть такой, - переводим в историю
        dcUK.doc.MODIFIED = now('-')
        dcUK.doc.MODIFIER = dcUK.fullName
    else:
        dcUK.doc.CREATED = now('-')
        dcUK.doc.CREATOR = dcUK.fullName

    # сохраняем новый док(или новую версию)
    if dcUK.doc.root:
        r = dcUK.doc.root

        s = ''
        for i in range(1000, 9001, 1000):
            s += dcUK.doc[f'ROOT_STYLES_{i}'] + '_¤_'

        fs = len(r) + len(s)
        r = zlib.compress(r.encode(), 9)
        r = str(base64.b64encode(r), 'ascii')
        s = zlib.compress(s.encode(), 9)
        s = str(base64.b64encode(s), 'ascii')

        dcUK.doc.root = f'{r}_¤_{s}'

        le64 = len(r) + len(s)
        le = f'fullsize:{fs} => zip => b64:{le64}'
        proc = int(100 * (fs - le64) / (fs or le64))
        dcUK.doc.pageSize = le
        snd(f'{le} (doc {dcUK.doc.docNo} in "{dcUK.dbAlias}") press:{proc}%', cat='ROOT-size')

    fi = {k:v.replace("'", "''") for k, v in dcUK.doc.items() if v and k != 'UNID'}
    xfi = json.dumps(fi, ensure_ascii=False)

    if dcUK.update or not dcUK.dbAlias.lower().endswith('draft'):  # делаем историю только для *DRAFT.sqlite
        if oldDoc:
            sql = [f"UPDATE LIFE SET xfld='{xfi}' WHERE (unid='{unid}') AND (xmdf IS NULL);"]
        else:
            sql = [f"INSERT INTO LIFE (unid, xfld, xmdf) VALUES ('{unid}', '{xfi}', NULL);"]
    else:
        sql = [
            f"UPDATE LIFE SET xmdf='{datetime.now()}' WHERE (unid='{unid}') AND (xmdf IS NULL);",
            f"INSERT INTO LIFE (unid, xfld, xmdf) VALUES ('{unid}', '{xfi}', NULL);",
        ]

    con = connectToSrv(dcUK.dbAlias)
    if not con:
        return

    cur = con.cursor()
    for s in sql:
        try:
            cur.execute(s)
        except Exception as ex:
            err(f'can not execute SQL statement. Exception: {ex}, SQL: {s}', cat='docSaveDB')
            with suppress(Exception):
                cur and cur.close()
                con.rollback()
                unlockCon(con, dcUK.dbAlias)
            return

    try:
        cur.close()
        con.commit()
        unlockCon(con, dcUK.dbAlias)
        return True
    except Exception as ex:
        unlockCon(con, dcUK.dbAlias)
        err(f'{ex}', cat='docSaveDB-commit')

# *** *** ***


# @sndErr
def allFromDB(dbAlias, dir_=None):
    """
    возвращает все документы из таблицы
    """

    con = connectToSrv(dbAlias)
    if not con:
        return []

    sql = 'SELECT id, unid, xfld FROM LIFE WHERE (xmdf IS NULL);'

    cur = con.cursor()
    cursor = cur.execute(sql) or []

    docs = []
    for row in cursor:
        fields = json.loads(row[2])
        fields['UNID'] = row[1]
        fields['ID'] = row[0]
        if fields['UNID'] == 'new':
            continue
        if dir_ and dir_ != 'ALL' and fields.get('DIR') != dir_:
            continue

        if 'ROOT' in fields:
            root, _, styles = fields['ROOT'].partition('_¤_')
            try:
                fields['ROOT'] = zlib.decompress(base64.b64decode(root)).decode()
            except Exception as ex:
                err(f'{ex}', cat='ROO-decompress')
                fields['ROOT'] = '{"boxIndex": 100}'
            try:
                fields['ROOT_STYLES'] = styles and zlib.decompress(base64.b64decode(styles)).decode()
                styles = styles and zlib.decompress(base64.b64decode(styles)).decode()
                styles = (styles + ('_¤_' * 9)).split('_¤_')
                for i in range(9):
                    if styles[i]:
                        fields[f'ROOT_STYLES_{(i+1)*1000}'] = styles[i]
            except Exception as ex:
                err(f'{ex}', cat='ROOT_STYLES-decompress')
                fields['ROOT_STYLES'] = ''

        docs.append(DC(fields))

    cur.close()
    unlockCon(con, dbAlias)

    return docs

# *** *** ***


def snoDB(dcUK):
    dbAlias = dcUK.dbAlias
    n = setDocNo(dbAlias) or ''
    if n:
        snd(f'{dcUK.fullName}: зарегистрирован номер {n} в {dbAlias}', cat='Регистрация')
    else:
        err(f'{dcUK.fullName}: номер не сохранен в {dbAlias} из-за ошибки', cat='Регистрация')
    return n

# *** *** ***


def setDocNo(dbAlias):
    table = 'appAll_docno'
    docNoAlias = 'docno'
    con = connectToSrv(docNoAlias)
    if not con:
        return

    try:
        sql = f"SELECT docno FROM {table} WHERE dbalias='{dbAlias}';"
        cur = con.cursor()
        cursor = cur.execute(sql)
        n = 0
        if cursor:
            for row in cursor:
                n = row[0]
        else:
            unlockCon(con, docNoAlias)
            err(f'for {dbAlias} cur.execute == None', cat='setDocNo')
            return

        if n:
            sql = f"UPDATE {table} SET docno={n+1} WHERE dbalias='{dbAlias}';"
        else:
            sql = f"INSERT INTO {table} (dbalias, docno) VALUES ('{dbAlias}', 1);"

        cur.execute(sql)
        cur.close()
        con.commit()
        unlockCon(con, docNoAlias)
        return str(n + 1)

    except Exception as ex:
        err(f'{ex}', cat='setDocNo')
        unlockCon(con, docNoAlias)

# *** *** ***


def fff(doc, fn='FILES'):  # fields for files
    return [ k for k, v in doc.items()
                if k.startswith(fn) and ('_' in k) and v.count('|') == 5
        ]


def filines(doc, fn='FILES'):
        return [f'{doc.F(k)}|{k}'.split('|') for k in fff(doc, fn)]

# *** *** **


def histFromDB(dcUK):
    """
    возвращает все времена переведов в историю
    """

    con = connectToSrv(dcUK.dbAlias)
    if not con:
        return []
    unid = dcUK.unid.replace('-', '')

    sql = f"SELECT xmdf, xfld FROM LIFE WHERE (unid == '{unid}') AND (xmdf IS NOT NULL);"

    cur = con.cursor()
    cursor = cur.execute(sql) or []

    hist = []

    for row in cursor:
        xfld = row[1] or '{}'

        fields = json.loads(xfld)
        ls = fields.get('MODIFIER', fields.get('CREATOR', '')).partition(' ')
        mdf = f'{ls[0]} {ls[2] and ls[2][0]}'
        s1, _, size2 = fields.get('PAGESIZE', '').rpartition(':')
        size1 = s1.partition(':')[2].partition(' ')[0]
        hist.append(f"{row[0]} ({mdf}, size:{size1}->{size2}) {fields.get('NOTES', '')}")

    cur.close()
    unlockCon(con, dcUK.dbAlias)

    hist = sorted(hist)
    for i, h in enumerate(hist):
        hist[i] = f'{i+1:03}__{h}'

    return json.dumps(hist)

if __name__ == '__main__':
    createDB('rf.qq/ogg')

