# -*- coding: utf-8 -*-
"""
AON 2020
"""

from arm.tools.first import err
from arm.tools.DC import toWell

import re, os
from datetime import datetime
import traceback

import uuid
import base64
import hashlib

# *** *** ***

sovaOnline = 'sova.online'

# *** *** ***

busyFunc = {}

# *** *** ***


def cleanPhone(phone):
    phone = re.sub(r'[^\d]', '', phone)
    if phone:
        return '+7' + phone[1:] if phone[0] == '8' else '+' + phone
    return ''


def generate_cv_code():
    code_verifier = f'{uuid.uuid4()}-{uuid.uuid4()}'
    toWell(code_verifier, 'code_verifier')

    hash_object = hashlib.sha256(code_verifier.encode())
    hash_bytes = hash_object.digest()
    b64_encoded_hash = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').rstrip('=')
        
    code_challenge = f'{b64_encoded_hash}'
    
    return code_challenge

# *** *** ***


def checkBusy(func):
    """
    Декоратор, блокирующий повторный вызов функции.
    """

    def _wrapper(*args, **kwargs):
        if not busyFunc.get(func.__name__):
            try:
                busyFunc[func.__name__] = True
                func(*args, **kwargs)
            except Exception as ex:
                err(f'{func.__name__}: {ex}', cat='amgrRun.checkBusy')
            finally:
                busyFunc[func.__name__] = False

    return _wrapper

# *** *** ***


def now(dlm='.'):
    if dlm == '.':
        return datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    elif dlm == '_':
        return datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
    else:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # if dlm == '.':
        # return datetime.now(tz=get_current_timezone()).strftime('%d.%m.%Y %H:%M:%S')
    # else:
        # return datetime.now(tz=get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')

# *** *** ***


def today(dlm='.'):
    if dlm == '.':
        return datetime.today().strftime('%d.%m.%Y')
    else:
        return datetime.today().strftime('%Y-%m-%d')

# *** *** ***

js_search = re.compile(r'((<script[\s]+src[\s]*)|(<link[\s]+rel[\s]*))=[\s]*[\'"][\s\S]+?(\.css"|\.js"|\.json")', re.IGNORECASE | re.M | re.U)

def setVersionJS(bf, path):
    """
bf =
...
<script src="/api/jsv?lb.js"></script>
<link rel="stylesheet" href="jsv?std3d.css"/>

returned:
...
[
<script src="/api/jsv?lb.js::2013-09-02 09:57:24"></script>
<link rel="stylesheet" href="/api/jsv?std3d.css::2013-08-29 13:16:28"/>
, ver
]
    """
    itr = js_search.finditer(bf)
    l0 = 0
    bf2 = ''
    ver = ''
    for match in itr:
        s = match.group()
        if 'jsv?' in s:
            s = s[:-1]
            fn = os.path.join(path, s.partition('jsv?')[2])
            try:
                stat = os.stat(fn)
                v = datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y-%H:%M:%S')
                s += '::' + v
                ver = max(ver, v)
            except Exception as ex:
                s = s.replace('jsv?', 'js?')
                err(f'\nfn:"{fn}" not found\n{ex}', cat='setVersionJS')

        s += '"'

        l1, l2 = match.span()
        bf2 += bf[l0:l1] + s
        l0 = l2

    return bf2 + bf[l0:], ver

# *** *** ***


def setVersionFiles(ls, path):
    ols = []
    if ls:
        if type(ls) is str:
            ls = [ls]
        for s in ls:
            if 'jsv?' not in s:
                s and ols.append(s)
            else:
                fn = os.path.join(path, s.partition('jsv?')[2])
                try:
                    stat = os.stat(fn)
                    v = datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y-%H:%M:%S')
                    ols.append(s + '::' + v)
                except:
                    err(f'"{fn}" not found', cat='setVersionFiles')
    return ols

# *** *** ***


def sndErr(func):
    """
    Декоратор. Вызывает функцию func и ловит Exception.
    Если поймал:
        - выводит имя функции и сообщение об ошибке
        - возвращает None.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            err(f'{ex}\n{traceback.format_exc()}', cat=f'Y-{func.__name__}')

    return wrapper

# *** *** ***


def setLevel(inh, d):

    def incAA(s):  # увеличивает заданный в s o_level
        if len(s) < 3 or not('.aa' <= s < '.zz'):
            return '.aa'

        if ord(s[2]) < ord('z'):
            return '.' + s[1] + chr(ord(s[2]) + 1)
        else:
            return '.' + chr(ord(s[1]) + 1) + 'a'

    # *** *** ***

    dic = {}
    first = d.form[0].lower()

    for r in d.db.getResponses(d.ref):
        if r.form.split('.')[0] == d.form and r.o_level and r.dir != 'd':
            dic[r.o_level] = r

    if not dic:
        return first + '.aa'

    sk = sorted(dic.keys())

    if not (inh.ref and inh.o_level):
        return first + incAA(sk[-1][1:])

    io_level = inh.o_level
    lol = len(io_level)

    for i in range(len(sk)):
        if io_level == dic[sk[i]].o_level[:lol]:  # ищем свою ветку

            while i < len(sk):
                if io_level != dic[sk[i]].o_level[:lol]:  # своя ветка кончилась ?
                    if io_level == dic[sk[i - 1]].F('o_level'):
                        return io_level + '.aa'
                    return io_level + incAA(sk[i - 1][lol:])

                i += 1

            if io_level == dic[sk[i - 1]].o_level:
                return io_level + '.aa'
            return io_level + incAA(sk[i - 1][lol:])

    return first + incAA(sk[-1][1:])

# *** *** ***


user_regex = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
    re.IGNORECASE)
domain_regex = re.compile(
    r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z',
    re.IGNORECASE)


def emailValidator(value):
    user_part, _, domain_part = value.partition('@')
    return user_regex.match(user_part) and domain_regex.match(domain_part)

# *** *** ***

